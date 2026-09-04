from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "b76544528ff0"
down_revision: Union[str, Sequence[str], None] = "e2b28228dd70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # refresh_tokens is already created by c1a2b3c4d5e6.
    pass


def downgrade() -> None:
    # Nothing to undo here.
    pass
