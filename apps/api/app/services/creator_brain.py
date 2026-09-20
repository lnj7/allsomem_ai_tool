from typing import Any

from sqlalchemy.orm import Session

from app.ai.agents.future import MonetizationAgent, OnboardingAgent, PlatformAnalysisAgent
from app.db.models.domain import (
    BrandProfile,
    ContentPillar,
    Creator,
    CreatorGoal,
    CreatorProfile,
    TargetAudience,
)
from app.services.social_account_service import SocialAccountService
from app.services.youtube_service import YouTubeService


class CreatorBrainService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_creator_context(self, creator: Creator) -> dict[str, Any]:
        goals = self._db.query(CreatorGoal).filter(CreatorGoal.creator_id == creator.id).all()
        audiences = (
            self._db.query(TargetAudience).filter(TargetAudience.creator_id == creator.id).all()
        )
        brand = (
            self._db.query(BrandProfile).filter(BrandProfile.creator_id == creator.id).one_or_none()
        )
        pillars = self._db.query(ContentPillar).filter(ContentPillar.creator_id == creator.id).all()
        profile = (
            self._db.query(CreatorProfile)
            .filter(CreatorProfile.creator_id == creator.id)
            .one_or_none()
        )
        return {
            "identity": {
                "display_name": creator.display_name,
                "creator_type": creator.creator_type,
                "niche": creator.niche,
                "bio": creator.bio,
                "language": creator.primary_language,
                "location": creator.location,
            },
            "onboarding": creator.onboarding_data,
            "goals": [
                {"type": g.goal_type, "description": g.description, "target": g.target_value}
                for g in goals
            ],
            "audiences": [
                {
                    "name": a.name,
                    "description": a.description,
                    "age_range": a.age_range,
                    "geography": a.geography,
                    "interests": a.interests,
                    "pain_points": a.pain_points,
                }
                for a in audiences
            ],
            "brand": None
            if brand is None
            else {
                "positioning": brand.positioning,
                "tone": brand.tone,
                "personality": brand.personality,
                "communication_style": brand.communication_style,
            },
            "pillars": [
                {"name": p.name, "description": p.description, "percentage": p.percentage}
                for p in pillars
            ],
            "accepted_profile": None if profile is None else profile.profile,
            "creator_stage": creator.creator_stage,
            "monetization_status": creator.monetization_status,
            "connected_accounts": SocialAccountService(self._db).list_accounts(creator),
            "platform_analysis": PlatformAnalysisAgent().analyze(
                SocialAccountService(self._db).list_accounts(creator)
            ),
            "onboarding_summary": OnboardingAgent().summarize(creator.onboarding_data or {}),
            "monetization": MonetizationAgent().workspace(
                {"monetization_status": creator.monetization_status}
            ),
            "youtube": YouTubeService(self._db).get(creator),
        }
