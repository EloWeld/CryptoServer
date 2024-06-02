

import json
from config import SETTINGS_FILE


def load_settings():
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)