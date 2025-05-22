"""added order to item stats

Revision ID: 12830c975d59
Revises: 5c7d691d5d36
Create Date: 2025-05-22 15:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '12830c975d59'
down_revision: Union[str, None] = '5c7d691d5d36'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the column as nullable first
    op.add_column('item_stats', sa.Column('order', sa.Integer(), nullable=True))
    
    # Update existing rows with their order
    # For each item, order its stats by their current order in the database
    connection = op.get_bind()
    items = connection.execute(text("SELECT DISTINCT item_key FROM item_stats")).fetchall()
    
    for (item_key,) in items:
        # Get all stats for this item in their current order
        stats = connection.execute(
            text("SELECT item_key, stat_name FROM item_stats WHERE item_key = :item_key"),
            {"item_key": item_key}
        ).fetchall()
        
        # Update each stat with its order
        for order, (item_key, stat_name) in enumerate(stats):
            connection.execute(
                text("UPDATE item_stats SET \"order\" = :order WHERE item_key = :item_key AND stat_name = :stat_name"),
                {"order": order, "item_key": item_key, "stat_name": stat_name}
            )
    
    # Now make the column NOT NULL
    op.alter_column('item_stats', 'order',
               existing_type=sa.Integer(),
               nullable=False)


def downgrade() -> None:
    op.drop_column('item_stats', 'order')
