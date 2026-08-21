"""add chat history

Revision ID: ddcb7a39a33e
Revises: 0bd6b48fb8c3
Create Date: 2026-08-21 22:19:12.846095

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ddcb7a39a33e"
down_revision: Union[str, Sequence[str], None] = "0bd6b48fb8c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create chat conversation and message tables."""

    op.create_table(
        "chat_conversations",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "owner_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["owner_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_chat_conversations_owner_id"),
        "chat_conversations",
        ["owner_id"],
        unique=False,
    )

    op.create_table(
        "chat_messages",
        sa.Column(
            "id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "conversation_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["chat_conversations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_chat_messages_conversation_id"),
        "chat_messages",
        ["conversation_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove chat conversation and message tables."""

    op.drop_index(
        op.f("ix_chat_messages_conversation_id"),
        table_name="chat_messages",
    )

    op.drop_table("chat_messages")

    op.drop_index(
        op.f("ix_chat_conversations_owner_id"),
        table_name="chat_conversations",
    )

    op.drop_table("chat_conversations")