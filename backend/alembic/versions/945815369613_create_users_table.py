"""create users table

Revision ID: 945815369613
Revises:
Create Date: 2026-08-14 13:51:10.493378
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# =========================================================
# REVISION
# =========================================================

revision: str = "945815369613"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# =========================================================
# UPGRADE
# =========================================================

def upgrade() -> None:
    """Create users table."""

    op.create_table(
        "users",

        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),

        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
        ),

        sa.Column(
            "email",
            sa.String(length=255),
            nullable=True,
        ),

        sa.Column(
            "phone",
            sa.String(length=20),
            nullable=True,
        ),

        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=False,
        ),

        sa.Column(
            "role",
            sa.Enum(
                "CUSTOMER",
                "VENDOR",
                "OPERATOR",
                "ADMIN",
                name="userrole",
            ),
            nullable=False,
        ),

        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),

        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
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

    op.create_index(
        "ix_users_id",
        "users",
        ["id"],
        unique=False,
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True,
    )

    op.create_index(
        "ix_users_phone",
        "users",
        ["phone"],
        unique=True,
    )


# =========================================================
# DOWNGRADE
# =========================================================

def downgrade() -> None:
    """Drop users table."""

    op.drop_index(
        "ix_users_phone",
        table_name="users",
    )

    op.drop_index(
        "ix_users_email",
        table_name="users",
    )

    op.drop_index(
        "ix_users_id",
        table_name="users",
    )

    op.drop_table("users")