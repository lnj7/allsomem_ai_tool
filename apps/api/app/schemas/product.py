from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=200)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    full_name: str
    is_active: bool


class CreatorOut(BaseModel):
    id: UUID
    display_name: str
    creator_type: str | None
    niche: str | None
    bio: str | None
    primary_language: str | None
    timezone: str | None
    location: str | None
    onboarding_step: int
    onboarding_completed: bool
    onboarding_data: dict[str, Any]


class CreatorUpdate(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    niche: str | None = None
    primary_language: str | None = None
    timezone: str | None = None
    location: str | None = None


class OnboardingPayload(BaseModel):
    step: int = Field(ge=1, le=6)
    data: dict[str, Any]
    complete: bool = False


class AudienceBlock(BaseModel):
    description: str
    pain_points: list[str]
    interests: list[str]


class ContentPillarBlock(BaseModel):
    name: str
    description: str
    percentage: int = Field(ge=0, le=100)


class CreatorProfileSchema(BaseModel):
    niche: str
    positioning: str
    audience: AudienceBlock
    brand_personality: list[str]
    tone: str
    content_pillars: list[ContentPillarBlock]
    content_strategy: str
    recommended_formats: list[str]
    recommended_platforms: list[str]
    initial_strategy: list[str]


class GeneratedProfileOut(BaseModel):
    status: str
    profile: CreatorProfileSchema
    model: str | None = None
    prompt_version: str | None = None


class ProfileUpdateRequest(BaseModel):
    profile: CreatorProfileSchema
    accept: bool = False


class ContentGenerateRequest(BaseModel):
    topic: str | None = None
    platform: str | None = None
    format: str | None = None
    goal: str | None = None


class ContentAssetOut(BaseModel):
    id: UUID
    title: str
    script: str | None
    caption: str | None
    hashtags: list[Any]
    status: str
    scheduled_at: datetime | None
    asset_type: str


class ScheduleRequest(BaseModel):
    scheduled_at: datetime
    platform: str = "manual"


class CommentCreate(BaseModel):
    author_name: str
    body: str
    platform: str | None = None


class CommentReply(BaseModel):
    reply: str


class SettingsUpdate(BaseModel):
    approval_mode: str = Field(pattern="^(MANUAL|REVIEW_REQUIRED|AUTO_APPROVE)$")


class AssistantAsk(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class YouTubeConnectRequest(BaseModel):
    url: str = Field(min_length=2, max_length=500)
