"""add vendor_profiles table

Revision ID: fea0f31a3b8b
Revises: 945815369613
Create Date: 2026-08-29 20:32:48.572200

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "fea0f31a3b8b"
down_revision: Union[str, Sequence[str], None] = "945815369613"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "vendor_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("business_name", sa.String(length=150), nullable=False),
        sa.Column("business_type", sa.String(length=100), nullable=True),
        sa.Column("gst_number", sa.String(length=20), nullable=True),
        sa.Column("bank_account_number", sa.String(length=30), nullable=True),
        sa.Column("bank_ifsc", sa.String(length=15), nullable=True),
        sa.Column(
            "kyc_status",
            sa.Enum(
                "PENDING",
                "APPROVED",
                "REJECTED",
                name="kycstatus",
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_vendor_profiles_id",
        "vendor_profiles",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_vendor_profiles_user_id",
        "vendor_profiles",
        ["user_id"],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_vendor_profiles_user_id",
        table_name="vendor_profiles",
    )
    op.drop_index(
        "ix_vendor_profiles_id",
        table_name="vendor_profiles",
    )
    op.drop_table("vendor_profiles")