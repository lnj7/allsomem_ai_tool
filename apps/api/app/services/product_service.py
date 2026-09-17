from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.ai.agents.content import ContentAgent
from app.ai.agents.profile import CreatorProfileAgent
from app.ai.providers.base import AINotConfiguredError, AIProviderError
from app.ai.providers.openai_compatible import OpenAICompatibleProvider
from app.core.config import Settings
from app.db.models.domain import (
    AssistantMessage,
    AutomationSettings,
    BrandProfile,
    CommunityComment,
    ContentAsset,
    ContentIdea,
    ContentPillar,
    Creator,
    CreatorGoal,
    CreatorProfile,
    PublishingJob,
    TargetAudience,
)
from app.schemas.product import (
    ContentGenerateRequest,
    CreatorProfileSchema,
    CreatorUpdate,
    GeneratedProfileOut,
    OnboardingPayload,
)
from app.services.creator_brain import CreatorBrainService


class ProductService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self._db = db
        self._settings = settings
        self._brain = CreatorBrainService(db)

    def update_creator(self, creator: Creator, payload: CreatorUpdate) -> Creator:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(creator, field, value)
        self._db.commit()
        self._db.refresh(creator)
        return creator

    def save_onboarding(self, creator: Creator, payload: OnboardingPayload) -> Creator:
        data = dict(creator.onboarding_data or {})
        data.update(payload.data)
        creator.onboarding_data = data
        creator.onboarding_step = payload.step
        if payload.complete:
            creator.onboarding_completed = True
            self._persist_onboarding_entities(creator, data)
        self._db.commit()
        self._db.refresh(creator)
        return creator

    def generate_profile(self, creator: Creator) -> GeneratedProfileOut:
        provider = OpenAICompatibleProvider(self._settings)
        agent = CreatorProfileAgent(provider)
        context = self._brain.get_creator_context(creator)
        try:
            profile = agent.generate_profile(context)
        except AINotConfiguredError as exc:
            raise HTTPException(status_code=503, detail="AI provider is not configured.") from exc
        except AIProviderError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        row = (
            self._db.query(CreatorProfile)
            .filter(CreatorProfile.creator_id == creator.id)
            .one_or_none()
        )
        if row is None:
            row = CreatorProfile(
                creator_id=creator.id, profile=profile.model_dump(), status="draft"
            )
            self._db.add(row)
        row.profile = profile.model_dump()
        row.status = "draft"
        row.model = self._settings.ai_model
        row.prompt_version = agent.prompt_version
        self._apply_profile_to_creator(creator, profile)
        self._db.commit()
        return GeneratedProfileOut(
            status=row.status,
            profile=profile,
            model=row.model,
            prompt_version=row.prompt_version,
        )

    def get_profile(self, creator: Creator) -> GeneratedProfileOut | None:
        row = (
            self._db.query(CreatorProfile)
            .filter(CreatorProfile.creator_id == creator.id)
            .one_or_none()
        )
        if row is None:
            return None
        return GeneratedProfileOut(
            status=row.status,
            profile=CreatorProfileSchema.model_validate(row.profile),
            model=row.model,
            prompt_version=row.prompt_version,
        )

    def update_profile(
        self, creator: Creator, profile: CreatorProfileSchema, accept: bool
    ) -> GeneratedProfileOut:
        row = (
            self._db.query(CreatorProfile)
            .filter(CreatorProfile.creator_id == creator.id)
            .one_or_none()
        )
        if row is None:
            row = CreatorProfile(creator_id=creator.id, profile=profile.model_dump())
            self._db.add(row)
        row.profile = profile.model_dump()
        if accept:
            row.status = "accepted"
            row.accepted_at = datetime.now(UTC)
        self._apply_profile_to_creator(creator, profile)
        self._db.commit()
        return GeneratedProfileOut(
            status=row.status, profile=profile, model=row.model, prompt_version=row.prompt_version
        )

    def generate_content(self, creator: Creator, request: ContentGenerateRequest) -> ContentAsset:
        provider = OpenAICompatibleProvider(self._settings)
        agent = ContentAgent(provider)
        context = self._brain.get_creator_context(creator)
        try:
            generated = agent.generate(context, request.model_dump())
        except AINotConfiguredError as exc:
            raise HTTPException(status_code=503, detail="AI provider is not configured.") from exc
        except AIProviderError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        idea = ContentIdea(
            creator_id=creator.id,
            title=generated.title,
            description=generated.hook,
            format=generated.format,
            target_platform=generated.platform,
            objective=generated.objective,
            hook=generated.hook,
            status="ready",
        )
        self._db.add(idea)
        self._db.flush()
        asset = ContentAsset(
            creator_id=creator.id,
            content_idea_id=idea.id,
            asset_type=generated.format or "post",
            title=generated.title,
            script=generated.script,
            caption=f"{generated.caption}\n\n{generated.cta}".strip(),
            hashtags=generated.hashtags,
            status="READY",
        )
        self._db.add(asset)
        self._db.commit()
        self._db.refresh(asset)
        return asset

    def list_assets(self, creator: Creator) -> list[ContentAsset]:
        return (
            self._db.query(ContentAsset)
            .filter(ContentAsset.creator_id == creator.id)
            .order_by(ContentAsset.created_at.desc())
            .all()
        )

    def list_ideas(self, creator: Creator) -> list[ContentIdea]:
        return (
            self._db.query(ContentIdea)
            .filter(ContentIdea.creator_id == creator.id)
            .order_by(ContentIdea.created_at.desc())
            .all()
        )

    def schedule_asset(
        self, creator: Creator, asset_id: UUID, scheduled_at: datetime, platform: str
    ) -> ContentAsset:
        asset = self._get_asset(creator, asset_id)
        settings = self._settings_for(creator)
        asset.scheduled_at = scheduled_at
        if settings.approval_mode == "AUTO_APPROVE":
            asset.status = "SCHEDULED"
        else:
            asset.status = "READY"
        job = PublishingJob(
            creator_id=creator.id,
            content_asset_id=asset.id,
            platform=platform,
            scheduled_at=scheduled_at,
            status="SCHEDULED" if asset.status == "SCHEDULED" else "READY",
            error_message="Social publishing is not configured. The item is saved locally only.",
        )
        self._db.add(job)
        self._db.commit()
        self._db.refresh(asset)
        return asset

    def approve_asset(self, creator: Creator, asset_id: UUID) -> ContentAsset:
        asset = self._get_asset(creator, asset_id)
        asset.status = "SCHEDULED" if asset.scheduled_at else "READY"
        self._db.commit()
        self._db.refresh(asset)
        return asset

    def dashboard(self, creator: Creator) -> dict:
        profile = self.get_profile(creator)
        assets = self.list_assets(creator)
        ready = [a for a in assets if a.status in {"READY", "SCHEDULED"}]
        settings = self._settings_for(creator)
        return {
            "creator_name": creator.display_name,
            "onboarding_completed": creator.onboarding_completed,
            "profile_status": None if profile is None else profile.status,
            "profile_completion": 100
            if creator.onboarding_completed and profile
            else 40
            if creator.onboarding_completed
            else 10,
            "followers": 0,
            "content_count": len(assets),
            "ready_count": len(ready),
            "approval_mode": settings.approval_mode,
            "today_plan": [{"title": a.title, "status": a.status} for a in ready[:3]],
            "ai_configured": bool(self._settings.ai_api_key.strip()),
        }

    def analytics_overview(self, creator: Creator) -> dict:
        return {
            "views": 0,
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "engagement_rate": 0,
            "followers": 0,
            "note": "Analytics appear after official platform integrations are connected. No sample metrics are shown.",
            "content_count": len(self.list_assets(creator)),
        }

    def list_comments(self, creator: Creator) -> list[CommunityComment]:
        return (
            self._db.query(CommunityComment)
            .filter(CommunityComment.creator_id == creator.id)
            .order_by(CommunityComment.created_at.desc())
            .all()
        )

    def add_comment(
        self, creator: Creator, author_name: str, body: str, platform: str | None
    ) -> CommunityComment:
        comment = CommunityComment(
            creator_id=creator.id, author_name=author_name, body=body, platform=platform
        )
        self._db.add(comment)
        self._db.commit()
        self._db.refresh(comment)
        return comment

    def reply_comment(self, creator: Creator, comment_id, reply: str) -> CommunityComment:
        comment = (
            self._db.query(CommunityComment)
            .filter(CommunityComment.id == comment_id, CommunityComment.creator_id == creator.id)
            .one_or_none()
        )
        if comment is None:
            raise HTTPException(status_code=404, detail="Comment not found.")
        comment.reply = reply
        comment.status = "replied"
        self._db.commit()
        self._db.refresh(comment)
        return comment

    def get_settings(self, creator: Creator) -> AutomationSettings:
        return self._settings_for(creator)

    def update_settings(self, creator: Creator, approval_mode: str) -> AutomationSettings:
        row = self._settings_for(creator)
        row.approval_mode = approval_mode
        self._db.commit()
        self._db.refresh(row)
        return row

    def brand_center(self, creator: Creator) -> dict:
        brand = (
            self._db.query(BrandProfile).filter(BrandProfile.creator_id == creator.id).one_or_none()
        )
        pillars = self._db.query(ContentPillar).filter(ContentPillar.creator_id == creator.id).all()
        profile = self.get_profile(creator)
        return {
            "display_name": creator.display_name,
            "brand": None
            if brand is None
            else {
                "positioning": brand.positioning,
                "tone": brand.tone,
                "personality": brand.personality,
                "communication_style": brand.communication_style,
                "preferred_language": brand.preferred_language,
            },
            "pillars": [
                {"name": p.name, "description": p.description, "percentage": p.percentage}
                for p in pillars
            ],
            "profile": None if profile is None else profile.profile.model_dump(),
        }

    def ask_assistant(self, creator: Creator, message: str) -> dict:
        self._db.add(AssistantMessage(creator_id=creator.id, role="user", content=message))
        provider = OpenAICompatibleProvider(self._settings)
        context = self._brain.get_creator_context(creator)
        prompt = (
            "You are the CreatorOS assistant. Be practical. Do not promise virality. "
            "Use this compact creator context:\n"
            f"{context}\n\nUser: {message}"
        )
        try:
            answer = provider.generate_text(prompt)
        except AINotConfiguredError as exc:
            raise HTTPException(status_code=503, detail="AI provider is not configured.") from exc
        except AIProviderError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        self._db.add(AssistantMessage(creator_id=creator.id, role="assistant", content=answer))
        self._db.commit()
        return {"reply": answer}

    def assistant_history(self, creator: Creator) -> list[dict]:
        rows = (
            self._db.query(AssistantMessage)
            .filter(AssistantMessage.creator_id == creator.id)
            .order_by(AssistantMessage.created_at.asc())
            .all()
        )
        return [
            {"role": row.role, "content": row.content, "created_at": row.created_at.isoformat()}
            for row in rows
        ]

    def _get_asset(self, creator: Creator, asset_id: UUID) -> ContentAsset:
        asset = (
            self._db.query(ContentAsset)
            .filter(ContentAsset.id == asset_id, ContentAsset.creator_id == creator.id)
            .one_or_none()
        )
        if asset is None:
            raise HTTPException(status_code=404, detail="Asset not found.")
        return asset

    def _settings_for(self, creator: Creator) -> AutomationSettings:
        row = (
            self._db.query(AutomationSettings)
            .filter(AutomationSettings.creator_id == creator.id)
            .one_or_none()
        )
        if row is None:
            row = AutomationSettings(creator_id=creator.id)
            self._db.add(row)
            self._db.commit()
            self._db.refresh(row)
        return row

    def _apply_profile_to_creator(self, creator: Creator, profile: CreatorProfileSchema) -> None:
        creator.niche = profile.niche
        creator.bio = profile.positioning
        brand = (
            self._db.query(BrandProfile).filter(BrandProfile.creator_id == creator.id).one_or_none()
        )
        if brand is None:
            brand = BrandProfile(creator_id=creator.id)
            self._db.add(brand)
        brand.positioning = profile.positioning
        brand.tone = profile.tone
        brand.personality = profile.brand_personality
        brand.communication_style = profile.content_strategy
        self._db.query(ContentPillar).filter(ContentPillar.creator_id == creator.id).delete()
        for index, pillar in enumerate(profile.content_pillars, start=1):
            self._db.add(
                ContentPillar(
                    creator_id=creator.id,
                    name=pillar.name,
                    description=pillar.description,
                    percentage=pillar.percentage,
                    priority=index,
                )
            )
        audience = (
            self._db.query(TargetAudience)
            .filter(TargetAudience.creator_id == creator.id)
            .one_or_none()
        )
        if audience is None:
            audience = TargetAudience(creator_id=creator.id, name="Primary audience")
            self._db.add(audience)
        audience.description = profile.audience.description
        audience.interests = profile.audience.interests
        audience.pain_points = profile.audience.pain_points

    def _persist_onboarding_entities(self, creator: Creator, data: dict) -> None:
        creator.display_name = str(data.get("name") or creator.display_name)
        creator.creator_type = data.get("creator_type")
        creator.bio = data.get("introduction")
        creator.primary_language = data.get("preferred_language")
        creator.location = data.get("geography")
        self._db.query(CreatorGoal).filter(CreatorGoal.creator_id == creator.id).delete()
        if data.get("primary_goal"):
            self._db.add(
                CreatorGoal(
                    creator_id=creator.id,
                    goal_type=str(data.get("primary_goal")),
                    description=str(data.get("primary_goal")),
                    target_value=str(data.get("desired_audience_size") or ""),
                    status="active",
                )
            )
        if data.get("secondary_goal"):
            self._db.add(
                CreatorGoal(
                    creator_id=creator.id,
                    goal_type=str(data.get("secondary_goal")),
                    description=str(data.get("secondary_goal")),
                    status="active",
                )
            )
        audience = (
            self._db.query(TargetAudience)
            .filter(TargetAudience.creator_id == creator.id)
            .one_or_none()
        )
        if audience is None:
            audience = TargetAudience(creator_id=creator.id, name="Primary audience")
            self._db.add(audience)
        audience.description = data.get("audience_who")
        audience.geography = data.get("geography")
        audience.age_range = data.get("age_group")
        audience.interests = _as_list(data.get("audience_interests"))
        audience.pain_points = _as_list(data.get("audience_problems"))
        brand = (
            self._db.query(BrandProfile).filter(BrandProfile.creator_id == creator.id).one_or_none()
        )
        if brand is None:
            brand = BrandProfile(creator_id=creator.id)
            self._db.add(brand)
        brand.tone = data.get("tone")
        brand.personality = _as_list(data.get("personality"))
        brand.communication_style = data.get("content_style")
        brand.preferred_language = data.get("preferred_language")


def _as_list(value: object) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [part.strip() for part in str(value).split(",") if part.strip()]
