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

@dataclass
class Settings(db.Model):
    id: int
    user_id: int
    webhooks: list
    received_hooks: list
    blocked_hooks: int
    domain: str
    pump_webhook: str
    dump_webhook: str
    pump_data: str
    dump_data: str
    enable_pump: bool
    enable_dump: bool
    check_per_minutes: int
    check_per_minutes_mode_2: int
    max_save_minutes: int
    price_change_percent: float
    price_change_trigger_percent: float
    oi_change_percent: float
    cvd_change_percent: float
    v_volumes_change_percent: float
    use_spot: bool
    use_wicks: bool
    tg_id: int
    
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), nullable=False)
    webhooks = sa.Column(sa.JSON, default=[])
    received_hooks = sa.Column(sa.JSON, default=[])
    blocked_hooks = sa.Column(sa.Integer, default=0)
    domain = sa.Column(sa.String(255), default="")
    pump_webhook = sa.Column(sa.String(255), default="")
    dump_webhook = sa.Column(sa.String(255), default="")
    pump_data = sa.Column(sa.Text, default="")
    dump_data = sa.Column(sa.Text, default="")
    enable_pump = sa.Column(sa.Boolean, default=False)
    enable_dump = sa.Column(sa.Boolean, default=False)
    check_per_minutes = sa.Column(sa.Integer, default=0)
    check_per_minutes_mode_2 = sa.Column(sa.Integer, default=0)
    max_save_minutes = sa.Column(sa.Integer, default=0)
    price_change_percent = sa.Column(sa.Float, default=0.0)
    price_change_trigger_percent = sa.Column(sa.Float, default=0.0)
    oi_change_percent = sa.Column(sa.Float, default=0.0)
    cvd_change_percent = sa.Column(sa.Float, default=0.0)
    v_volumes_change_percent = sa.Column(sa.Float, default=0.0)
    use_spot = sa.Column(sa.Boolean, default=False)
    use_wicks = sa.Column(sa.Boolean, default=False)
    tg_id = sa.Column(sa.BigInteger, default=0)
    
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
    id: int
    symbol: str
    price: float
    timestamp: datetime.datetime

    id = sa.Column(sa.Integer, primary_key=True)
    symbol = sa.Column(sa.String(50), nullable=False)
    price = sa.Column(sa.Float, nullable=False)
    timestamp = sa.Column(sa.DateTime, default=datetime.datetime.now)

@dataclass
class FuturesPrice(db.Model):
    id: int
    symbol: str
    price: float
    timestamp: datetime.datetime

    id = sa.Column(sa.Integer, primary_key=True)
    symbol = sa.Column(sa.String(50), nullable=False)
    price = sa.Column(sa.Float, nullable=False)
    timestamp = sa.Column(sa.DateTime, default=datetime.datetime.now)