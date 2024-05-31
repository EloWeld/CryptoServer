

import os
from dotenv import load_dotenv


load_dotenv()

SETTINGS_FILE = 'settings_new.json'
CHANGES_LOG_FILE = 'changes_log.txt'
PRICE_SAVE_FILE = 'binance_prices.csv'

COINGLASS_SECRET = os.environ.get("COINGLASS_SECRET", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")