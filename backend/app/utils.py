
import datetime
import loguru
import requests

from config import Config

global_cvd = {}


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


def get_oi_candles_minutes(symbol: str, period_minutes):

    limit = max(1, period_minutes // 5)

    url = 'https://fapi.binance.com/futures/data/openInterestHist'
    response = requests.get(url, params={
        "symbol": symbol,
        "period": "5m",
        "limit": limit,
    })

    c_time = datetime.datetime.now().timestamp() // 60

    if response.status_code == 200:
        prices = response.json()
        filled_prices = []
        for price in prices:
            timestamp = price['timestamp']
            oi_value = price['sumOpenInterest']
            # Заполняем каждую минуту в 5-минутном интервале одинаковыми данными
            for i in range(5):
                if (price['timestamp'] / 1000 // 60) + i + 1 > c_time:
                    continue
                filled_prices.append([
                    (price['timestamp'] / 1000 // 60) + i,
                    float(oi_value)
                ])
        return filled_prices[:period_minutes]  # Возвращаем только запрашиваемое количество минут
    else:
        loguru.logger.error(f"Error fetching data from Binance API , code: {response.status_code}, data: {response.text}")
        return None


def get_cvd(symbol, limit):
    # Запрос данных ордербука (глубина рынка)
    trades_response = requests.get(f"https://fapi.binance.com/fapi/v1/aggTrades", params={
        "symbol": symbol,
        "limit": 1000,
        "startTime": int((datetime.datetime.now() - datetime.timedelta(minutes=limit)).timestamp() * 1000)
    })
    trades = trades_response.json()
    cvd = []

    lm = 0
    for trade in trades:
        cm = trade['T'] // 1000 // 60
        curr_cvd = float(trade['q']) if trade['m'] else -float(trade['q'])
        if lm != cm:
            lm = cm
            cvd.append([cm, curr_cvd])
        else:
            cvd[-1][-1] += curr_cvd
    return cvd[-limit:]


def get_cvd_change(symbol, period):
    cvd = get_cvd(symbol)

    # Используем последние доступные данные, если недостаточно данных для заданного периода
    if len(cvd) < period:
        period = len(cvd)

    # Определение CVD для текущего периода и периода минут назад
    period_minutes_ago_cvd = cvd[-period][1]
    current_minutes_cvd = cvd[-1][1]

    return ((current_minutes_cvd - period_minutes_ago_cvd) / period_minutes_ago_cvd) * 100 if period_minutes_ago_cvd != 0 else 0


def get_volumes(symbol, limit=100):
    # Запрос данных ордербука (глубина рынка)
    klines_response = requests.get(f"https://fapi.binance.com/fapi/v1/klines", params={"symbol": symbol, "interval": "1m", "limit": limit})
    volumes = [[float(x[0] / 1000 // 60), float(x[5])] for x in sorted(klines_response.json(), key=lambda x: x[0])]
    return volumes


def get_volumes_change(symbol, limit=100):
    # Запрос данных ордербука (глубина рынка)
    volumes = get_volumes(symbol, limit)
    past_vol = float(volumes[0][1])
    current_vol = float(volumes[-1][1])

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
