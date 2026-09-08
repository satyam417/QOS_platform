"""add categories and services

Revision ID: 31960355f790
Revises: a20b5b4f9eeb
Create Date: 2026-09-07 12:21:43.415068

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "31960355f790"
down_revision: Union[str, Sequence[str], None] = "a20b5b4f9eeb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_index(
        "ix_categories_id",
        "categories",
        ["id"],
        unique=False,
    )

    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vendor_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "INACTIVE", name="servicestatus"),
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
            ["category_id"],
            ["categories.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["vendor_id"],
            ["vendor_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_services_category_id",
        "services",
        ["category_id"],
        unique=False,
    )

    op.create_index(
        "ix_services_id",
        "services",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_services_vendor_id",
        "services",
        ["vendor_id"],
        unique=False,
    )

    op.create_table(
        "service_pincodes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.Integer(), nullable=False),
        sa.Column("pincode", sa.String(length=6), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["service_id"],
            ["services.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "service_id",
            "pincode",
            name="uq_service_pincode",
        ),
    )

    op.create_index(
        "ix_service_pincodes_id",
        "service_pincodes",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_service_pincodes_pincode",
        "service_pincodes",
        ["pincode"],
        unique=False,
    )

    op.create_index(
        "ix_service_pincodes_service_id",
        "service_pincodes",
        ["service_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_service_pincodes_service_id",
        table_name="service_pincodes",
    )

    op.drop_index(
        "ix_service_pincodes_pincode",
        table_name="service_pincodes",
    )

    op.drop_index(
        "ix_service_pincodes_id",
        table_name="service_pincodes",
    )

    op.drop_table("service_pincodes")

    op.drop_index(
        "ix_services_vendor_id",
        table_name="services",
    )

    op.drop_index(
        "ix_services_id",
        table_name="services",
    )

    op.drop_index(
        "ix_services_category_id",
        table_name="services",
    )

    op.drop_table("services")

    op.drop_index(
        "ix_categories_id",
        table_name="categories",
    )

    op.drop_table("categories")