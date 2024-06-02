import loguru
import requests
from config import BOT_TOKEN
from global_utils import load_settings

settings = load_settings()

def spam_all(message, kb=None):
    for user_id in settings['tg_users']:
        try:
            data = {
                "chat_id": user_id,
                "text": message,
                "parse_mode": "HTML",
            }
            if kb:
                data["reply_markup"] = kb
            resp = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', json=data)
            print(resp.json())
        except Exception as e:
            loguru.logger.error(str(e))


if __name__ == "__main__":
    spam_all("Hello mr davinchi!")