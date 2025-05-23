"""merge_heads

Revision ID: 0caec197d067
Revises: 2b5360e2266e, refactor_item_models
Create Date: 2025-05-23 16:57:09.691183

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0caec197d067'
down_revision: Union[str, None] = ('2b5360e2266e', 'refactor_item_models')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
