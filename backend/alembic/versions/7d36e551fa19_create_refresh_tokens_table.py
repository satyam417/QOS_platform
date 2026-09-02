"""create refresh tokens table

Revision ID: 7d36e551fa19
Revises: 945815369613
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7d36e551fa19"
down_revision: Union[str, Sequence[str], None] = "945815369613"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_refresh_tokens_user_id",
        "refresh_tokens",
        ["user_id"],
        unique=False,
    )

    op.create_index(
        "ix_refresh_tokens_token_hash",
        "refresh_tokens",
        ["token_hash"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_refresh_tokens_token_hash",
        table_name="refresh_tokens",
    )

    op.drop_index(
        "ix_refresh_tokens_user_id",
        table_name="refresh_tokens",
    )

    op.drop_table("refresh_tokens")