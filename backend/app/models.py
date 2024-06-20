from dataclasses import dataclass
import datetime
from . import db
from flask_login import UserMixin
import sqlalchemy as sa


class User(UserMixin, db.Model):
    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(150), unique=True, nullable=False)
    password = sa.Column(sa.String(150), nullable=False)
    timezone_offset = sa.Column(sa.Integer, default=0)
    settings = db.relationship('Settings', backref='user', uselist=False)
    changes_log = db.relationship('ChangesLog', backref='user', lazy=True)
    parsings_process = db.relationship('ParsingProcess', backref='user', lazy=True)


@dataclass
class ParsingProcess(db.Model):
    id: int
    user_id: int
    started_at: datetime.datetime
    ended_at: datetime.datetime
    status: str

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=False)
    status = sa.Column(sa.String(150), nullable=False, default="active")
    started_at = sa.Column(sa.DateTime, nullable=False, default=datetime.datetime.now)
    ended_at = sa.Column(sa.DateTime, default=None, nullable=True)


@dataclass
class Settings(db.Model):
    id: int
    user_id: int
    webhooks: list
    received_hooks: list
    blocked_hooks: int
    domain: str

    check_per_minutes_rapid: int
    rapid_delay: str
    rapid_pump_webhook: str
    rapid_dump_webhook: str
    rapid_pump_data: str
    rapid_dump_data: str
    rapid_enable_pump: bool
    rapid_enable_dump: bool

    check_per_minutes_smooth: int
    smooth_delay: str
    smooth_pump_webhook: str
    smooth_dump_webhook: str
    smooth_pump_data: str
    smooth_dump_data: str
    smooth_enable_pump: bool
    smooth_enable_dump: bool

    reverse_rapid_pump_data: str
    reverse_rapid_dump_data: str
    reverse_rapid_enable_pump: bool
    reverse_rapid_enable_dump: bool
    reverse_smooth_pump_data: str
    reverse_smooth_dump_data: str
    reverse_smooth_enable_pump: bool
    reverse_smooth_enable_dump: bool

    default_vol_usd: float
    reverse_vol_usd: float
    reverse_last_order_dist: float
    reverse_full_orders_count: int
    reverse_orders_count: int
    reverse_multiplier: float
    reverse_density: float

    price_change_percent: float
    price_change_trigger_percent: float
    max_save_minutes: int
    oi_change_percent: float
    cvd_change_percent: float
    v_volumes_change_percent: float
    tg_id: int

    use_wicks: bool
    use_spot: bool
    use_only_usdt: bool
    coins_blacklist: list[str]

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=False)
    webhooks = sa.Column(sa.JSON, default=[])
    received_hooks = sa.Column(sa.JSON, default=[])
    blocked_hooks = sa.Column(sa.Integer, default=0)
    domain = sa.Column(sa.String(255), default="https://www.davinchi-crypto.ru/api")

    check_per_minutes_rapid = sa.Column(sa.Integer, default=0)
    rapid_delay = sa.Column(sa.Integer(), default=3)
    rapid_pump_webhook = sa.Column(sa.String(255), default="https://hook.finandy.com/?")
    rapid_dump_webhook = sa.Column(sa.String(255), default="https://hook.finandy.com/?")
    rapid_pump_data = sa.Column(sa.Text, default="{}")
    rapid_dump_data = sa.Column(sa.Text, default="{}")
    rapid_enable_pump = sa.Column(sa.Boolean, default=True)
    rapid_enable_dump = sa.Column(sa.Boolean, default=True)

    check_per_minutes_smooth = sa.Column(sa.Integer, default=0)
    smooth_delay = sa.Column(sa.Integer(), default=3)
    smooth_pump_webhook = sa.Column(sa.String(255), default="https://hook.finandy.com/?")
    smooth_dump_webhook = sa.Column(sa.String(255), default="https://hook.finandy.com/?")
    smooth_pump_data = sa.Column(sa.Text, default="{}")
    smooth_dump_data = sa.Column(sa.Text, default="{}")
    smooth_enable_pump = sa.Column(sa.Boolean, default=True)
    smooth_enable_dump = sa.Column(sa.Boolean, default=True)

    reverse_rapid_pump_data = sa.Column(sa.Text, default="{}")
    reverse_rapid_dump_data = sa.Column(sa.Text, default="{}")
    reverse_rapid_enable_pump = sa.Column(sa.Boolean, default=True)
    reverse_rapid_enable_dump = sa.Column(sa.Boolean, default=True)
    reverse_smooth_pump_data = sa.Column(sa.Text, default="{}")
    reverse_smooth_dump_data = sa.Column(sa.Text, default="{}")
    reverse_smooth_enable_pump = sa.Column(sa.Boolean, default=True)
    reverse_smooth_enable_dump = sa.Column(sa.Boolean, default=True)

    default_vol_usd = sa.Column(sa.Float, default=1.0)
    reverse_vol_usd = sa.Column(sa.Float, default=1.0)
    reverse_last_order_dist = sa.Column(sa.Float, default=8.0)
    reverse_full_orders_count = sa.Column(sa.Integer, default=10)
    reverse_orders_count = sa.Column(sa.Integer, default=8)
    reverse_multiplier = sa.Column(sa.Float, default=1.5)
    reverse_density = sa.Column(sa.Float, default=0.7)

    price_change_percent = sa.Column(sa.Float, default=0.0)
    price_change_trigger_percent = sa.Column(sa.Float, default=0.0)

    max_save_minutes = sa.Column(sa.Integer, default=0)
    oi_change_percent = sa.Column(sa.Float, default=0.0)
    cvd_change_percent = sa.Column(sa.Float, default=0.0)
    v_volumes_change_percent = sa.Column(sa.Float, default=0.0)
    tg_id = sa.Column(sa.BigInteger, default=-1)

    coins_blacklist = sa.Column(sa.ARRAY(sa.String), nullable=False, default=[])
    use_only_usdt = sa.Column(sa.Boolean, default=False, nullable=False, server_default='false')
    use_spot = sa.Column(sa.Boolean, default=False)
    use_wicks = sa.Column(sa.Boolean, default=False)


@dataclass
class ChangesLog(db.Model):
    id: int
    user_id: int
    exchange: str
    symbol: str
    type: str
    mode: str
    change_amount: str
    interval: int
    old_price: float
    curr_price: float
    created_at: datetime
    additional_data: dict

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=False)
    exchange = sa.Column(sa.String(50), nullable=True)
    symbol = sa.Column(sa.String(50), nullable=True)
    type = sa.Column(sa.String(10), nullable=True)  # pump or dump
    mode = sa.Column(sa.String(20), nullable=True)
    change_amount = sa.Column(sa.String(10), nullable=True)
    interval = sa.Column(sa.Integer, nullable=True)
    old_price = sa.Column(sa.Float, nullable=True)
    curr_price = sa.Column(sa.Float, nullable=True)
    created_at = sa.Column(sa.DateTime, default=datetime.datetime.now)
    additional_data = sa.Column(sa.JSON, nullable=True)


@dataclass
class SpotPrice(db.Model):
    symbol: str
    price: float
    timestamp: datetime.datetime

    symbol = sa.Column(sa.String(50), nullable=False)
    price = sa.Column(sa.Float, nullable=False)
    timestamp = sa.Column(sa.DateTime, default=datetime.datetime.now)


@dataclass
class FuturesPrice(db.Model):
    symbol: str
    price: float
    timestamp: datetime.datetime

    symbol = sa.Column(sa.String(50), nullable=False)
    price = sa.Column(sa.Float, nullable=False)
    timestamp = sa.Column(sa.DateTime, default=datetime.datetime.now)
