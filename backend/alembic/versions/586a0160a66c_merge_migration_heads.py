"""merge migration heads

Revision ID: 586a0160a66c
Revises: b3a70234899e, c1a2b3c4d5e6, e2b28228dd70
Create Date: 2026-09-02 17:46:26.194818

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '586a0160a66c'
down_revision: Union[str, Sequence[str], None] = ('b3a70234899e', 'c1a2b3c4d5e6', 'e2b28228dd70')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
