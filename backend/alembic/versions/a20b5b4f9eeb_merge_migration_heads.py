"""merge migration heads

Revision ID: a20b5b4f9eeb
Revises: 3245b9080895, 586a0160a66c
Create Date: 2026-09-03 15:23:20.294220

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a20b5b4f9eeb'
down_revision: Union[str, Sequence[str], None] = ('3245b9080895', '586a0160a66c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
