"""Comment

Revision ID: 05ba5e784ac7
Revises: 
Create Date: 2024-07-11 18:27:17.927907

"""
import datetime
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '05ba5e784ac7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Создание таблицы User
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(150), unique=True, nullable=False),
        sa.Column('password', sa.String(150), nullable=False),
        sa.Column('timezone_offset', sa.Integer, default=0)
    )

    # Создание таблицы ParsingProcess
    op.create_table(
        'parsing_process',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id', ondelete='cascade'), nullable=False),
        sa.Column('status', sa.String(150), nullable=False, default="active"),
        sa.Column('started_at', sa.DateTime, nullable=False, default=datetime.datetime.now),
        sa.Column('ended_at', sa.DateTime, default=None, nullable=True)
    )

    # Создание таблицы Settings
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id', ondelete='cascade'), nullable=False),
        sa.Column('webhooks', sa.JSON, default=[]),
        sa.Column('received_hooks', sa.JSON, default=[]),
        sa.Column('blocked_hooks', sa.Integer, default=0),
        sa.Column('domain', sa.String(255), default="https://www.davinchi-crypto.ru/api"),
        sa.Column('check_per_minutes_rapid', sa.Integer, default=0),
        sa.Column('rapid_delay', sa.Integer(), default=3),
        sa.Column('rapid_pump_webhook', sa.String(255), default="https://hook.finandy.com/?"),
        sa.Column('reverse_rapid_pump_webhook', sa.String(255), default="https://hook.finandy.com/?"),
        sa.Column('rapid_dump_webhook', sa.String(255), default="https://hook.finandy.com/?"),
        sa.Column('reverse_rapid_dump_webhook', sa.String(255), default="https://hook.finandy.com/?"),
        sa.Column('rapid_pump_data', sa.Text, default="{}"),
        sa.Column('rapid_dump_data', sa.Text, default="{}"),
        sa.Column('rapid_enable_pump', sa.Boolean, default=True),
        sa.Column('rapid_enable_dump', sa.Boolean, default=True),
        sa.Column('check_per_minutes_smooth', sa.Integer, default=0),
        sa.Column('smooth_delay', sa.Integer(), default=3),
        sa.Column('smooth_pump_webhook', sa.String(255), default="https://hook.finandy.com/?"),
        sa.Column('reverse_smooth_pump_webhook', sa.String(255), default="https://hook.finandy.com/?"),
        sa.Column('smooth_dump_webhook', sa.String(255), default="https://hook.finandy.com/?"),
        sa.Column('reverse_smooth_dump_webhook', sa.String(255), default="https://hook.finandy.com/?"),
        sa.Column('smooth_pump_data', sa.Text, default="{}"),
        sa.Column('smooth_dump_data', sa.Text, default="{}"),
        sa.Column('smooth_enable_pump', sa.Boolean, default=True),
        sa.Column('smooth_enable_dump', sa.Boolean, default=True),
        sa.Column('reverse_rapid_pump_data', sa.Text, default="{}"),
        sa.Column('reverse_rapid_dump_data', sa.Text, default="{}"),
        sa.Column('reverse_rapid_enable_pump', sa.Boolean, default=True),
        sa.Column('reverse_rapid_enable_dump', sa.Boolean, default=True),
        sa.Column('reverse_smooth_pump_data', sa.Text, default="{}"),
        sa.Column('reverse_smooth_dump_data', sa.Text, default="{}"),
        sa.Column('reverse_smooth_enable_pump', sa.Boolean, default=True),
        sa.Column('reverse_smooth_enable_dump', sa.Boolean, default=True),
        sa.Column('default_vol_usd', sa.Float, default=1.0),
        sa.Column('reverse_vol_usd', sa.Float, default=1.0),
        sa.Column('reverse_last_order_dist', sa.Float, default=8.0),
        sa.Column('reverse_full_orders_count', sa.Integer, default=10),
        sa.Column('reverse_orders_count', sa.Integer, default=8),
        sa.Column('reverse_multiplier', sa.Float, default=1.5),
        sa.Column('reverse_density', sa.Float, default=0.7),
        sa.Column('price_change_percent', sa.Float, default=0.0),
        sa.Column('price_change_trigger_percent', sa.Float, default=0.0),
        sa.Column('max_save_minutes', sa.Integer, default=0),
        sa.Column('oi_change_percent', sa.Float, default=0.0),
        sa.Column('cvd_change_percent', sa.Float, default=0.0),
        sa.Column('v_volumes_change_percent', sa.Float, default=0.0),
        sa.Column('tg_id', sa.BigInteger, default=-1),
        sa.Column('coins_blacklist', sa.ARRAY(sa.String), nullable=False, default=[]),
        sa.Column('use_only_usdt', sa.Boolean, default=False, nullable=False, server_default='false'),
        sa.Column('use_spot', sa.Boolean, default=False),
        sa.Column('use_wicks', sa.Boolean, default=False)
    )

    # Создание таблицы ChangesLog
    op.create_table(
        'changes_log',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('user.id', ondelete='cascade'), nullable=False),
        sa.Column('exchange', sa.String(255), nullable=True),
        sa.Column('symbol', sa.String(50), nullable=True),
        sa.Column('type', sa.String(255), nullable=True),
        sa.Column('mode', sa.String(255), nullable=True),
        sa.Column('change_amount', sa.String(255), nullable=True),
        sa.Column('interval', sa.Integer, nullable=True),
        sa.Column('old_price', sa.Float, nullable=True),
        sa.Column('curr_price', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime, default=datetime.datetime.now),
        sa.Column('additional_data', sa.JSON, nullable=True)
    )

    # Создание таблицы SpotPrice
    op.create_table(
        'spot_price',
        sa.Column('id', sa.Integer, sa.Sequence('spot_price_id_seq', cycle=True), primary_key=True),
        sa.Column('symbol', sa.String(50), nullable=False),
        sa.Column('price', sa.Float, nullable=False),
        sa.Column('timestamp', sa.DateTime, default=datetime.datetime.now)
    )

    # Создание таблицы FuturesPrice
    op.create_table(
        'futures_price',
        sa.Column('id', sa.Integer, sa.Sequence('futures_price_id_seq', cycle=True), primary_key=True),
        sa.Column('symbol', sa.String(50), nullable=False),
        sa.Column('price', sa.Float, nullable=False),
        sa.Column('timestamp', sa.DateTime, default=datetime.datetime.now)
    )


def downgrade():
    # Удаление таблиц в обратном порядке
    op.drop_table('futures_price')
    op.drop_table('spot_price')
    op.drop_table('changes_log')
    op.drop_table('settings')
    op.drop_table('parsing_process')
    op.drop_table('user')