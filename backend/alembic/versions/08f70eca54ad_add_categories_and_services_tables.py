"""Add categories and services tables

Revision ID: 08f70eca54ad
Revises: f1e05460c0f5
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "08f70eca54ad"
down_revision: Union[str, Sequence[str], None] = "f1e05460c0f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create categories and services tables."""

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
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
    )

    op.create_index(
        "ix_categories_id",
        "categories",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_categories_name",
        "categories",
        ["name"],
        unique=True,
    )

    op.create_table(
        "services",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vendor_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
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
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["vendor_id"],
            ["vendor_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
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

    op.create_index(
        "ix_services_category_id",
        "services",
        ["category_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop categories and services tables."""

    op.drop_index(
        "ix_services_category_id",
        table_name="services",
    )

    op.drop_index(
        "ix_services_vendor_id",
        table_name="services",
    )

    op.drop_index(
        "ix_services_id",
        table_name="services",
    )

    op.drop_table("services")

    op.drop_index(
        "ix_categories_name",
        table_name="categories",
    )

    op.drop_index(
        "ix_categories_id",
        table_name="categories",
    )

    op.drop_table("categories")