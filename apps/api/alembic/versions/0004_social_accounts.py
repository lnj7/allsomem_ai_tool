"""multi-account social architecture

Revision ID: 0004_social_accounts
Revises: 0003_connected_platforms
Create Date: 2026-09-20
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_social_accounts"
down_revision: str | None = "0003_connected_platforms"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "creators",
        sa.Column("creator_stage", sa.String(length=20), server_default="BEGINNER", nullable=False),
    )
    op.add_column(
        "creators",
        sa.Column(
            "monetization_status", sa.String(length=40), server_default="UNKNOWN", nullable=False
        ),
    )
    op.create_table(
        "social_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("platform", sa.String(length=40), nullable=False),
        sa.Column("external_account_id", sa.String(length=200), nullable=False),
        sa.Column("account_name", sa.String(length=300), nullable=True),
        sa.Column("username", sa.String(length=200), nullable=True),
        sa.Column("account_type", sa.String(length=40), nullable=False),
        sa.Column("profile_url", sa.String(length=500), nullable=True),
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
        sa.Column("access_token_encrypted", sa.Text(), nullable=True),
        sa.Column("refresh_token_encrypted", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scopes", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("connection_status", sa.String(length=40), nullable=False),
        sa.Column("snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("connected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["creator_id"], ["creators.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "creator_id", "platform", "external_account_id", name="uq_social_accounts_creator_platform_external"
        ),
    )
    op.create_index("ix_social_accounts_creator_id", "social_accounts", ["creator_id"])
    op.create_table(
        "analytics_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("social_account_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("platform", sa.String(length=40), nullable=False),
        sa.Column("metric_name", sa.String(length=80), nullable=False),
        sa.Column("metric_value", sa.String(length=80), nullable=False),
        sa.Column("period", sa.String(length=40), nullable=True),
        sa.Column("source", sa.String(length=40), nullable=False),
        sa.Column("raw_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["creator_id"], ["creators.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["social_account_id"], ["social_accounts.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analytics_snapshots_creator_id", "analytics_snapshots", ["creator_id"])
    op.create_table(
        "ai_memory",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("memory_type", sa.String(length=80), nullable=False),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["creator_id"], ["creators.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ai_memory_creator_id", "ai_memory", ["creator_id"])
    op.create_table(
        "monetization_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("revenue_sources", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["creator_id"], ["creators.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("creator_id"),
    )
    op.create_table(
        "creator_stage_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_stage", sa.String(length=20), nullable=True),
        sa.Column("to_stage", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["creator_id"], ["creators.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_creator_stage_history_creator_id", "creator_stage_history", ["creator_id"])
    op.execute(
        """
        INSERT INTO social_accounts (
            id, creator_id, platform, external_account_id, account_name, username,
            account_type, profile_url, scopes, connection_status, snapshot,
            connected_at, last_synced_at, created_at, updated_at
        )
        SELECT
            gen_random_uuid(),
            creator_id,
            CASE WHEN lower(platform) = 'youtube' THEN 'YOUTUBE'
                 WHEN lower(platform) = 'instagram' THEN 'INSTAGRAM'
                 WHEN lower(platform) = 'facebook' THEN 'FACEBOOK'
                 ELSE upper(platform) END,
            external_id,
            title,
            handle,
            'CHANNEL',
            url,
            '[]'::jsonb,
            'PUBLIC_SNAPSHOT',
            snapshot,
            synced_at,
            synced_at,
            created_at,
            updated_at
        FROM connected_platforms
        WHERE NOT EXISTS (
            SELECT 1 FROM social_accounts s
            WHERE s.creator_id = connected_platforms.creator_id
              AND s.external_account_id = connected_platforms.external_id
        )
        """
    )


def downgrade() -> None:
    op.drop_index("ix_creator_stage_history_creator_id", table_name="creator_stage_history")
    op.drop_table("creator_stage_history")
    op.drop_table("monetization_profiles")
    op.drop_index("ix_ai_memory_creator_id", table_name="ai_memory")
    op.drop_table("ai_memory")
    op.drop_index("ix_analytics_snapshots_creator_id", table_name="analytics_snapshots")
    op.drop_table("analytics_snapshots")
    op.drop_index("ix_social_accounts_creator_id", table_name="social_accounts")
    op.drop_table("social_accounts")
    op.drop_column("creators", "monetization_status")
    op.drop_column("creators", "creator_stage")
