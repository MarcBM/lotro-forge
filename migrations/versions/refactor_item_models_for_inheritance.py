"""refactor item models for inheritance

Revision ID: refactor_item_models
Revises: 12830c975d59
Create Date: 2024-03-19 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'refactor_item_models'
down_revision: Union[str, None] = '12830c975d59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    # Create the enum type if it doesn't exist
    conn.execute(sa.text("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'item_quality') THEN
                CREATE TYPE item_quality AS ENUM ('common', 'uncommon', 'rare', 'incomparable', 'legendary');
            END IF;
        END$$;
    """))

    # Create items table with quality as string
    op.create_table(
        'items',
        sa.Column('key', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('base_ilvl', sa.Integer(), nullable=False),
        sa.Column('quality', sa.String(), nullable=False),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('item_type', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('key')
    )
    
    # Create equipment_items table
    op.create_table(
        'equipment_items',
        sa.Column('key', sa.Integer(), nullable=False),
        sa.Column('slot', sa.String(), nullable=False),
        sa.Column('armour_type', sa.String(), nullable=True),
        sa.Column('scaling', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['key'], ['items.key'], ),
        sa.PrimaryKeyConstraint('key')
    )
    
    # Create indexes
    op.create_index(op.f('ix_items_key'), 'items', ['key'], unique=False)
    op.create_index(op.f('ix_items_name'), 'items', ['name'], unique=False)
    op.create_index(op.f('ix_items_base_ilvl'), 'items', ['base_ilvl'], unique=False)
    op.create_index(op.f('ix_items_quality'), 'items', ['quality'], unique=False)
    op.create_index(op.f('ix_equipment_items_key'), 'equipment_items', ['key'], unique=False)
    op.create_index(op.f('ix_equipment_items_slot'), 'equipment_items', ['slot'], unique=False)
    
    # Migrate data from item_definitions to items and equipment_items
    conn.execute(sa.text("""
        INSERT INTO items (key, name, base_ilvl, quality, icon, item_type)
        SELECT key, name, base_ilvl, quality, icon, 'equipment'
        FROM item_definitions
    """))
    conn.execute(sa.text("""
        INSERT INTO equipment_items (key, slot, armour_type, scaling)
        SELECT key, slot, armour_type, scaling
        FROM item_definitions
    """))
    
    # Normalize quality values to lowercase before altering column type
    op.execute("UPDATE items SET quality = LOWER(quality);")
    # Now alter quality column to enum type
    op.execute("ALTER TABLE items ALTER COLUMN quality TYPE item_quality USING quality::item_quality;")
    
    # Update foreign keys in item_stats
    op.drop_constraint('item_stats_item_key_fkey', 'item_stats', type_='foreignkey')
    op.create_foreign_key(None, 'item_stats', 'items', ['item_key'], ['key'])
    
    # Drop old table
    op.drop_table('item_definitions')

def downgrade() -> None:
    conn = op.get_bind()
    # Recreate item_definitions table
    op.create_table(
        'item_definitions',
        sa.Column('key', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('base_ilvl', sa.Integer(), nullable=False),
        sa.Column('quality', sa.String(), nullable=False),
        sa.Column('slot', sa.String(), nullable=False),
        sa.Column('armour_type', sa.String(), nullable=True),
        sa.Column('scaling', sa.String(), nullable=True),
        sa.Column('icon', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('key')
    )
    
    # Create indexes
    op.create_index(op.f('ix_item_definitions_key'), 'item_definitions', ['key'], unique=False)
    op.create_index(op.f('ix_item_definitions_name'), 'item_definitions', ['name'], unique=False)
    op.create_index(op.f('ix_item_definitions_base_ilvl'), 'item_definitions', ['base_ilvl'], unique=False)
    op.create_index(op.f('ix_item_definitions_quality'), 'item_definitions', ['quality'], unique=False)
    op.create_index(op.f('ix_item_definitions_slot'), 'item_definitions', ['slot'], unique=False)
    
    # Migrate data back
    conn.execute(sa.text("""
        INSERT INTO item_definitions (key, name, base_ilvl, quality, slot, armour_type, scaling, icon)
        SELECT i.key, i.name, i.base_ilvl, i.quality, e.slot, e.armour_type, e.scaling, i.icon
        FROM items i
        JOIN equipment_items e ON i.key = e.key
        WHERE i.item_type = 'equipment'
    """))
    
    # Update foreign keys in item_stats
    op.drop_constraint('item_stats_item_key_fkey', 'item_stats', type_='foreignkey')
    op.create_foreign_key(None, 'item_stats', 'item_definitions', ['item_key'], ['key'])
    
    # Drop new tables
    op.drop_table('equipment_items')
    op.drop_table('items') 