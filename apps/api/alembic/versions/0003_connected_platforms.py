"""connected public platforms

Revision ID: 0003_connected_platforms
Revises: 0002_product_tables
Create Date: 2026-09-17
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_connected_platforms"
down_revision: str | None = "0002_product_tables"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "connected_platforms",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("platform", sa.String(length=40), nullable=False),
        sa.Column("external_id", sa.String(length=120), nullable=False),
        sa.Column("handle", sa.String(length=120), nullable=True),
        sa.Column("title", sa.String(length=300), nullable=True),
        sa.Column("url", sa.String(length=500), nullable=True),
        sa.Column("snapshot", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("synced_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["creator_id"], ["creators.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("creator_id", "platform", name="uq_connected_platforms_creator_platform"),
    )
    op.create_index("ix_connected_platforms_creator_id", "connected_platforms", ["creator_id"])


def downgrade() -> None:
    op.drop_index("ix_connected_platforms_creator_id", table_name="connected_platforms")
    op.drop_table("connected_platforms")
