"""remove_bio_column_from_users

Revision ID: e336f51dd809
Revises: d52c84f608f4
Create Date: 2025-06-05 11:10:25.131275

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e336f51dd809'
down_revision: Union[str, None] = 'd52c84f608f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'bio')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('bio', sa.VARCHAR(length=500), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
