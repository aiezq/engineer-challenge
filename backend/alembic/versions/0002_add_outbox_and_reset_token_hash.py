"""add outbox and reset_token_hash

Revision ID: 0002_add_outbox_and_reset_token_hash
Revises: 0001_initial_auth_schema
Create Date: 2026-03-08 00:10:00
"""

import hashlib

from alembic import op
import sqlalchemy as sa


revision = "0002_add_outbox_and_reset_token_hash"
down_revision = "0001_initial_auth_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("reset_token_hash", sa.String(), nullable=True))
    op.create_index("ix_users_reset_token_hash", "users", ["reset_token_hash"], unique=False)

    connection = op.get_bind()
    users = list(connection.execute(sa.text("SELECT id, reset_token FROM users WHERE reset_token IS NOT NULL")))
    for user_id, legacy_token in users:
        token_hash = hashlib.sha256(str(legacy_token).encode("utf-8")).hexdigest()
        connection.execute(
            sa.text("UPDATE users SET reset_token_hash = :token_hash WHERE id = :user_id"),
            {"token_hash": token_hash, "user_id": user_id},
        )

    op.create_table(
        "outbox_messages",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("event_version", sa.Integer(), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_outbox_messages_status", "outbox_messages", ["status"], unique=False)
    op.create_index("ix_outbox_messages_available_at", "outbox_messages", ["available_at"], unique=False)
    op.create_index("ix_outbox_messages_event_type", "outbox_messages", ["event_type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_outbox_messages_event_type", table_name="outbox_messages")
    op.drop_index("ix_outbox_messages_available_at", table_name="outbox_messages")
    op.drop_index("ix_outbox_messages_status", table_name="outbox_messages")
    op.drop_table("outbox_messages")
    op.drop_index("ix_users_reset_token_hash", table_name="users")
    op.drop_column("users", "reset_token_hash")
