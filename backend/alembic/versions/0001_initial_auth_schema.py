"""initial auth schema

Revision ID: 0001_initial_auth_schema
Revises:
Create Date: 2026-03-08 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial_auth_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reset_token", sa.String(), nullable=True),
        sa.Column("reset_token_expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_reset_token", "users", ["reset_token"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_users_reset_token", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
