from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fea0f31a3b8b"
down_revision: Union[str, Sequence[str], None] = "945815369613"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vendor_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("business_name", sa.String(), nullable=False),
        sa.Column("business_type", sa.String(), nullable=True),
        sa.Column("gst_number", sa.String(), nullable=True),
        sa.Column("bank_account_number", sa.String(), nullable=True),
        sa.Column("bank_ifsc", sa.String(), nullable=True),
        sa.Column("kyc_status", sa.String(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
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
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_vendor_profiles_user_id",
        table_name="vendor_profiles",
    )

    op.drop_index(
        "ix_vendor_profiles_id",
        table_name="vendor_profiles",
    )

    op.drop_table("vendor_profiles")