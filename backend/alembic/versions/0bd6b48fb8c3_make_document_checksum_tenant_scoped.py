"""Make document checksum tenant scoped.

Revision ID: 0bd6b48fb8c3
Revises: f75c50d13928
"""

from typing import Sequence, Union

from alembic import op


revision: str = "0bd6b48fb8c3"
down_revision: Union[str, Sequence[str], None] = "f75c50d13928"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Make checksum uniqueness tenant scoped."""

    # Remove global UNIQUE(checksum).
    op.drop_index(
        "ix_documents_checksum",
        table_name="documents",
    )

    # Enforce uniqueness per owner.
    op.create_unique_constraint(
        "uq_documents_owner_checksum",
        "documents",
        ["owner_id", "checksum"],
    )

    # Keep checksum indexed for lookups.
    op.create_index(
        "ix_documents_checksum",
        "documents",
        ["checksum"],
        unique=False,
    )


def downgrade() -> None:
    """Restore global checksum uniqueness."""

    op.drop_index(
        "ix_documents_checksum",
        table_name="documents",
    )

    op.drop_constraint(
        "uq_documents_owner_checksum",
        "documents",
        type_="unique",
    )

    op.create_index(
        "ix_documents_checksum",
        "documents",
        ["checksum"],
        unique=True,
    )