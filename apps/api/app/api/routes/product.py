from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth_deps import get_current_creator, get_current_user
from app.core.config import get_settings
from app.db.models.domain import Creator
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.product import (
    AssistantAsk,
    CommentCreate,
    CommentReply,
    ContentAssetOut,
    ContentGenerateRequest,
    CreatorOut,
    CreatorUpdate,
    GeneratedProfileOut,
    OnboardingPayload,
    ProfileUpdateRequest,
    ScheduleRequest,
    SettingsUpdate,
)
from app.services.product_service import ProductService

router = APIRouter(prefix="/api/v1", tags=["product"])


def _service(db: Session = Depends(get_db)) -> ProductService:
    return ProductService(db, get_settings())


@router.get("/creators/me", response_model=CreatorOut)
def get_creator(creator: Creator = Depends(get_current_creator)) -> Creator:
    return creator


@router.put("/creators/me", response_model=CreatorOut)
def update_creator(
    payload: CreatorUpdate,
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> Creator:
    return service.update_creator(creator, payload)


@router.get("/onboarding")
def get_onboarding(creator: Creator = Depends(get_current_creator)) -> dict:
    return {
        "step": creator.onboarding_step,
        "completed": creator.onboarding_completed,
        "data": creator.onboarding_data,
    }


@router.post("/onboarding")
def save_onboarding(
    payload: OnboardingPayload,
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> dict:
    saved = service.save_onboarding(creator, payload)
    return {
        "step": saved.onboarding_step,
        "completed": saved.onboarding_completed,
        "data": saved.onboarding_data,
    }


@router.post("/onboarding/generate-profile", response_model=GeneratedProfileOut)
def generate_profile(
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> GeneratedProfileOut:
    return service.generate_profile(creator)


@router.get("/strategy")
def get_strategy(
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> GeneratedProfileOut | dict:
    profile = service.get_profile(creator)
    if profile is None:
        return {"status": "missing", "profile": None}
    return profile


@router.post("/strategy/generate", response_model=GeneratedProfileOut)
def generate_strategy(
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> GeneratedProfileOut:
    return service.generate_profile(creator)


@router.put("/strategy", response_model=GeneratedProfileOut)
def update_strategy(
    payload: ProfileUpdateRequest,
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> GeneratedProfileOut:
    return service.update_profile(creator, payload.profile, payload.accept)


@router.get("/dashboard")
def dashboard(
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> dict:
    return service.dashboard(creator)


@router.get("/content/ideas")
def content_ideas(
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> list[dict]:
    return [
        {
            "id": str(idea.id),
            "title": idea.title,
            "hook": idea.hook,
            "platform": idea.target_platform,
            "format": idea.format,
            "status": idea.status,
        }
        for idea in service.list_ideas(creator)
    ]


@router.post("/content/ideas")
def create_idea_alias(
    payload: ContentGenerateRequest,
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> ContentAssetOut:
    asset = service.generate_content(creator, payload)
    return ContentAssetOut.model_validate(asset, from_attributes=True)


@router.post("/content/generate")
def generate_content(
    payload: ContentGenerateRequest,
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> ContentAssetOut:
    asset = service.generate_content(creator, payload)
    return ContentAssetOut.model_validate(asset, from_attributes=True)


@router.get("/content/assets")
def list_assets(
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> list[ContentAssetOut]:
    return [
        ContentAssetOut.model_validate(asset, from_attributes=True)
        for asset in service.list_assets(creator)
    ]


@router.post("/content/assets/{asset_id}/schedule")
def schedule_asset(
    asset_id: UUID,
    payload: ScheduleRequest,
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> ContentAssetOut:
    asset = service.schedule_asset(creator, asset_id, payload.scheduled_at, payload.platform)
    return ContentAssetOut.model_validate(asset, from_attributes=True)


@router.post("/content/assets/{asset_id}/approve")
def approve_asset(
    asset_id: UUID,
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> ContentAssetOut:
    return ContentAssetOut.model_validate(
        service.approve_asset(creator, asset_id), from_attributes=True
    )


@router.get("/analytics/overview")
def analytics(
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> dict:
    return service.analytics_overview(creator)


@router.get("/community/comments")
def comments(
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> list[dict]:
    return [
        {
            "id": str(item.id),
            "author_name": item.author_name,
            "body": item.body,
            "platform": item.platform,
            "status": item.status,
            "reply": item.reply,
            "created_at": item.created_at.isoformat(),
        }
        for item in service.list_comments(creator)
    ]


@router.post("/community/comments")
def add_comment(
    payload: CommentCreate,
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> dict:
    item = service.add_comment(creator, payload.author_name, payload.body, payload.platform)
    return {"id": str(item.id), "status": item.status}


@router.post("/community/comments/{comment_id}/reply")
def reply_comment(
    comment_id: UUID,
    payload: CommentReply,
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> dict:
    item = service.reply_comment(creator, comment_id, payload.reply)
    return {"id": str(item.id), "reply": item.reply, "status": item.status}


@router.get("/brand-center")
def brand_center(
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> dict:
    return service.brand_center(creator)


@router.get("/settings")
def get_settings_route(
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> dict:
    row = service.get_settings(creator)
    return {"approval_mode": row.approval_mode}


@router.put("/settings")
def update_settings_route(
    payload: SettingsUpdate,
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> dict:
    row = service.update_settings(creator, payload.approval_mode)
    return {"approval_mode": row.approval_mode}


@router.get("/assistant/messages")
def assistant_history(
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> list[dict]:
    return service.assistant_history(creator)


@router.post("/assistant/ask")
def assistant_ask(
    payload: AssistantAsk,
    creator: Creator = Depends(get_current_creator),
    service: ProductService = Depends(_service),
) -> dict:
    return service.ask_assistant(creator, payload.message)


@router.get("/me")
def me_alias(user: User = Depends(get_current_user)) -> dict:
    return {"id": str(user.id), "email": user.email, "full_name": user.full_name}
