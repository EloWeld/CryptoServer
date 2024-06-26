"""Added reverse variables

Revision ID: e7d7053ebe99
Revises: 24ece299d5e3
Create Date: 2024-06-19 16:41:29.688028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e7d7053ebe99'
down_revision = '24ece299d5e3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('reverse_rapid_pump_data', sa.Text(), nullable=True))
    op.add_column('settings', sa.Column('reverse_rapid_dump_data', sa.Text(), nullable=True))
    op.add_column('settings', sa.Column('reverse_rapid_enable_pump', sa.Boolean(), nullable=True))
    op.add_column('settings', sa.Column('reverse_rapid_enable_dump', sa.Boolean(), nullable=True))
    op.add_column('settings', sa.Column('reverse_smooth_pump_data', sa.Text(), nullable=True))
    op.add_column('settings', sa.Column('reverse_smooth_dump_data', sa.Text(), nullable=True))
    op.add_column('settings', sa.Column('reverse_smooth_enable_pump', sa.Boolean(), nullable=True))
    op.add_column('settings', sa.Column('reverse_smooth_enable_dump', sa.Boolean(), nullable=True))
    op.add_column('settings', sa.Column('default_vol_usd', sa.Float(), nullable=True))
    op.add_column('settings', sa.Column('reverse_vol_usd', sa.Float(), nullable=True))
    op.add_column('settings', sa.Column('reverse_last_order_dist', sa.Float(), nullable=True))
    op.add_column('settings', sa.Column('reverse_full_orders_count', sa.Integer(), nullable=True))
    op.add_column('settings', sa.Column('reverse_orders_count', sa.Integer(), nullable=True))
    op.add_column('settings', sa.Column('reverse_multiplier', sa.Float(), nullable=True))
    op.add_column('settings', sa.Column('reverse_density', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('settings', 'reverse_density')
    op.drop_column('settings', 'reverse_multiplier')
    op.drop_column('settings', 'reverse_orders_count')
    op.drop_column('settings', 'reverse_full_orders_count')
    op.drop_column('settings', 'reverse_last_order_dist')
    op.drop_column('settings', 'reverse_vol_usd')
    op.drop_column('settings', 'default_vol_usd')
    op.drop_column('settings', 'reverse_smooth_enable_dump')
    op.drop_column('settings', 'reverse_smooth_enable_pump')
    op.drop_column('settings', 'reverse_smooth_dump_data')
    op.drop_column('settings', 'reverse_smooth_pump_data')
    op.drop_column('settings', 'reverse_rapid_enable_dump')
    op.drop_column('settings', 'reverse_rapid_enable_pump')
    op.drop_column('settings', 'reverse_rapid_dump_data')
    op.drop_column('settings', 'reverse_rapid_pump_data')
    # ### end Alembic commands ###
