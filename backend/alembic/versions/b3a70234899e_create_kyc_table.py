"""create kyc table

Revision ID: b3a70234899e
Revises: 945815369613
Create Date: 2026-08-26 18:22:45.803792

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b3a70234899e"
down_revision: Union[str, Sequence[str], None] = "945815369613"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create KYC table."""

    op.create_table(
        "kyc",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),

        sa.Column(
            "vendor_id",
            sa.Integer(),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),

        sa.Column(
            "document_type",
            sa.String(length=50),
            nullable=False,
        ),

        sa.Column(
            "document_path",
            sa.Text(),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.Enum(
                "PENDING",
                "APPROVED",
                "REJECTED",
                name="kycstatus",
            ),
            nullable=False,
            server_default="PENDING",
        ),

        sa.Column(
            "rejection_reason",
            sa.Text(),
            nullable=True,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Drop KYC table."""

    op.drop_table("kyc")