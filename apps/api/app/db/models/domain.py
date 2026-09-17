from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.models.user import User


class Creator(Base):
    __tablename__ = "creators"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    creator_type: Mapped[str | None] = mapped_column(String(50))
    niche: Mapped[str | None] = mapped_column(String(200))
    bio: Mapped[str | None] = mapped_column(Text)
    primary_language: Mapped[str | None] = mapped_column(String(80))
    timezone: Mapped[str | None] = mapped_column(String(80))
    location: Mapped[str | None] = mapped_column(String(200))
    onboarding_step: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default="1"
    )
    onboarding_completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    onboarding_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped[User] = relationship()


class CreatorGoal(Base):
    __tablename__ = "creator_goals"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    creator_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("creators.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    goal_type: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    target_value: Mapped[str | None] = mapped_column(String(80))
    current_value: Mapped[str | None] = mapped_column(String(80))
    target_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="active")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class TargetAudience(Base):
    __tablename__ = "target_audiences"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    creator_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("creators.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    age_range: Mapped[str | None] = mapped_column(String(80))
    geography: Mapped[str | None] = mapped_column(String(200))
    interests: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    pain_points: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    creator_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("creators.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    positioning: Mapped[str | None] = mapped_column(Text)
    brand_promise: Mapped[str | None] = mapped_column(Text)
    tone: Mapped[str | None] = mapped_column(String(120))
    personality: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    communication_style: Mapped[str | None] = mapped_column(Text)
    visual_style: Mapped[str | None] = mapped_column(Text)
    preferred_language: Mapped[str | None] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class ContentPillar(Base):
    __tablename__ = "content_pillars"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    creator_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("creators.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    percentage: Mapped[int | None] = mapped_column(Integer)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class CreatorProfile(Base):
    __tablename__ = "creator_profiles"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    creator_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("creators.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    profile: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="draft")
    model: Mapped[str | None] = mapped_column(String(120))
    prompt_version: Mapped[str | None] = mapped_column(String(80))
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class ContentIdea(Base):
    __tablename__ = "content_ideas"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    creator_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("creators.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    content_pillar_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("content_pillars.id", ondelete="SET NULL")
    )
    format: Mapped[str | None] = mapped_column(String(80))
    target_platform: Mapped[str | None] = mapped_column(String(80))
    objective: Mapped[str | None] = mapped_column(String(200))
    hook: Mapped[str | None] = mapped_column(Text)
    score: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="draft")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class ContentAsset(Base):
    __tablename__ = "content_assets"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    creator_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("creators.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content_idea_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("content_ideas.id", ondelete="SET NULL")
    )
    asset_type: Mapped[str] = mapped_column(String(40), nullable=False, default="post")
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    script: Mapped[str | None] = mapped_column(Text)
    caption: Mapped[str | None] = mapped_column(Text)
    hashtags: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    media_url: Mapped[str | None] = mapped_column(String(500))
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    extra_metadata: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="DRAFT")
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class PublishingJob(Base):
    __tablename__ = "publishing_jobs"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    creator_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("creators.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    content_asset_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("content_assets.id", ondelete="CASCADE"), nullable=False
    )
    platform: Mapped[str] = mapped_column(String(40), nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    platform_post_id: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="READY")
    error_message: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class CommunityComment(Base):
    __tablename__ = "community_comments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    creator_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("creators.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_name: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    platform: Mapped[str | None] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="inbox")
    reply: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class AutomationSettings(Base):
    __tablename__ = "automation_settings"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    creator_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("creators.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    approval_mode: Mapped[str] = mapped_column(
        String(40), nullable=False, default="REVIEW_REQUIRED"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class AssistantMessage(Base):
    __tablename__ = "assistant_messages"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    creator_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("creators.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
