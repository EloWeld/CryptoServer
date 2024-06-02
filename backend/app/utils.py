
import datetime
import loguru
import requests

from config import Config


def get_oi_candles(symbol: str, period):
    url = 'https://fapi.binance.com/futures/data/openInterestHist'
    response = requests.get(url, params={
        "symbol": symbol,
        "period": "5m",
        "limit": period,
    })

    if response.status_code == 200:
        prices = response.json()
        return prices
    else:
        loguru.logger.error(f"Error fetching data from Binance API , code: {response.status_code}, data: {response.text}")
        return None


def get_cvd_change(symbol, period):
    # Запрос агрегированных сделок за последние три минуты
    trades_response = requests.get(f"https://fapi.binance.com/fapi/v1/trades", params={
        "symbol": symbol,
        "limit": 1000,
    })
    trades = trades_response.json()

    # Фильтрация сделок за последние три минуты
    past_trades = [trade for trade in trades if (period-1) * 60 <= (datetime.datetime.now() - datetime.datetime.fromtimestamp(trade['time']/1000)).seconds < period * 60]
    current_trades = [trade for trade in trades if (datetime.datetime.now() - datetime.datetime.fromtimestamp(trade['time']/1000)).seconds <= 60]
    # Расчёт CVD 3 минуты назад
    past_cvd = sum(float(trade['qty']) if trade['isBuyerMaker'] else -float(trade['qty']) for trade in past_trades)

    # Расчёт текущего CVD
    current_cvd = sum(float(trade['qty']) if trade['isBuyerMaker'] else -float(trade['qty']) for trade in current_trades)

    return ((current_cvd - past_cvd) / past_cvd) * 100 if past_cvd != 0 else float('inf')


def get_volumes_change(symbol, limit=100):
    # Запрос данных ордербука (глубина рынка)
    klines_response = requests.get(f"https://fapi.binance.com/fapi/v1/klines", params={"symbol": symbol, "interval": "1m", "limit": limit})
    volumes = [x[5] for x in sorted(klines_response.json(), key=lambda x: x[0])]
    past_vol = float(volumes[0])
    current_vol = float(volumes[-1])

    return ((current_vol - past_vol) / past_vol) * 100 if past_vol != 0 else float('inf')


def get_futures_prices():
    url = 'https://fapi.binance.com/fapi/v2/ticker/price'
    response = requests.get(url)

    if response.status_code == 200:
        prices = response.json()
        return prices
    else:
        loguru.logger.error(f"Error fetching data from Binance API , code: {response.status_code}, data: {response.text}")
        return None


def get_spot_prices():
    url = 'https://api.binance.com/api/v3/ticker/price'
    response = requests.get(url)

    if response.status_code == 200:
        prices = response.json()
        return prices
    else:
        loguru.logger.error(f"Error fetching data from Binance API , code: {response.status_code}, data: {response.text}")
        return None
    
def send_tg_message(tg_id, message, kb=None):
    data = {
        "chat_id": tg_id,
        "text": message,
        "parse_mode": "HTML",
    }
    if kb:
        data["reply_markup"] = kb
    resp = requests.post(f'https://api.telegram.org/bot{Config.BOT_TOKEN}/sendMessage', json=data)
    print(resp.json())
