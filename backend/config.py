

from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://username:password@localhost/db_name')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'max_overflow': 30,
        'pool_recycle': 3600
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SETTINGS_FILE = 'settings_new.json'
    CHANGES_LOG_FILE = 'changes_log.txt'
    PRICE_SAVE_FILE = 'binance_prices.csv'

    COINGLASS_SECRET = os.environ.get("COINGLASS_SECRET", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
