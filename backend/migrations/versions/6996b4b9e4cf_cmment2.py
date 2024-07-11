"""Cmment2

Revision ID: 6996b4b9e4cf
Revises: 05ba5e784ac7
Create Date: 2024-07-11 18:32:38.205269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6996b4b9e4cf'
down_revision = '05ba5e784ac7'
branch_labels = None
depends_on = None


def upgrade():
    # Добавление новых полей
    op.add_column('settings', sa.Column('reverse_rapid_pump_webhook', sa.String(255), nullable=True, server_default="https://hook.finandy.com/?"))
    op.add_column('settings', sa.Column('reverse_rapid_dump_webhook', sa.String(255), nullable=True, server_default="https://hook.finandy.com/?"))
    op.add_column('settings', sa.Column('reverse_smooth_pump_webhook', sa.String(255), nullable=True, server_default="https://hook.finandy.com/?"))
    op.add_column('settings', sa.Column('reverse_smooth_dump_webhook', sa.String(255), nullable=True, server_default="https://hook.finandy.com/?"))


def downgrade():
    # Удаление новых полей
    op.drop_column('settings', 'reverse_rapid_pump_webhook')
    op.drop_column('settings', 'reverse_rapid_dump_webhook')
    op.drop_column('settings', 'reverse_smooth_pump_webhook')
    op.drop_column('settings', 'reverse_smooth_dump_webhook')