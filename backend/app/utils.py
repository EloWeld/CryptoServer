
import datetime
import time
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
            oi_value = price['sumOpenInterestValue']
            # Заполняем каждую минуту в 5-минутном интервале одинаковыми данными
            for i in range(5):
                if (price['timestamp'] / 1000 // 60) + i > c_time:
                    continue
                filled_prices.append([
                    (price['timestamp'] / 1000 // 60) + i,
                    float(oi_value)
                ])
        return filled_prices[:period_minutes]  # Возвращаем только запрашиваемое количество минут
    else:
        loguru.logger.error(f"Error fetching data from Binance API , code: {response.status_code}, data: {response.text}")
        return None


def normalize_data(data):
    min_val = min(data)
    max_val = max(data)
    normalized_data = [(x - min_val) / (max_val - min_val) * 200 - 100 for x in data]
    return normalized_data


def get_cvd(symbol, limit):
    end_time = int(datetime.datetime.now().timestamp() * 1000)
    start_time = end_time - limit * 60 * 1000  # Начальное время для первого запроса
    cvd = []
    attempts = 0

    while len(cvd) < limit and attempts < 30:
        trades_response = requests.get(f"https://fapi.binance.com/fapi/v1/aggTrades", params={
            "symbol": symbol,
            "limit": 1000,
            "startTime": start_time,
            "endTime": end_time
        })

        if trades_response.status_code == 418:
            time.sleep(5)  # Ждем 5 секунд, если получен статус код 418
            attempts += 1
            continue

        trades = trades_response.json()

        if not trades:
            break

        lm = cvd[-1][0] if cvd else 0
        for trade in trades:
            if isinstance(trade, str):
                loguru.logger.error(f"CVD is STR, trades: {trades}")
                continue
            cm = trade['T'] // 1000 // 60
            curr_cvd = float(trade['q']) if trade['m'] else -float(trade['q'])
            if lm != cm:
                lm = cm
                cvd.append([cm, curr_cvd])
            else:
                cvd[-1][-1] += curr_cvd
        attempts += 1

        if len(cvd) >= limit:
            cvd = cvd[-limit:]  # Обрезаем до нужного лимита
            break

        # Обновляем start_time для следующего запроса
        start_time = trades[-1]['T'] + 1  # Начинаем со следующей миллисекунды после последней сделки

    return cvd


def get_cvd_change(symbol, period):
    cvd = get_cvd(symbol, period)
    cvd_values = [float(cvd_entry[1]) for cvd_entry in cvd]

    # Нормализация значений CVD
    normalized_cvd = normalize_data(cvd_values)

    # Определение CVD для текущего периода и периода минут назад
    period_minutes_ago_cvd = normalized_cvd[-period]
    current_minutes_cvd = normalized_cvd[-1]

    return ((current_minutes_cvd - period_minutes_ago_cvd) / abs(period_minutes_ago_cvd)) * 100 if period_minutes_ago_cvd != 0 else 0


def get_volumes(symbol, limit=100):
    # Запрос данных ордербука (глубина рынка)
    klines_response = requests.get(f"https://fapi.binance.com/fapi/v1/klines", params={"symbol": symbol, "interval": "1m", "limit": limit})
    volumes = [[float(x[0] / 1000 // 60), float(x[5])] for x in sorted(klines_response.json(), key=lambda x: x[0])]
    return volumes


def get_volumes_change(symbol, limit=100):
    # Запрос данных ордербука (глубина рынка)
    volumes = get_volumes(symbol, limit)
    volume_values = [float(volume[1]) for volume in volumes]

    # Нормализация значений объема
    normalized_volumes = normalize_data(volume_values)

    past_vol = normalized_volumes[0]
    current_vol = normalized_volumes[-1]

    return ((current_vol - past_vol) / abs(past_vol)) * 100 if past_vol != 0 else float('inf')


def get_binance_future_symbols():
    url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    response = requests.get(url)
    data = response.json()

    symbols = [symbol['symbol'] for symbol in data['symbols']]
    return symbols


def get_binance_spot_symbols():
    url = "https://api.binance.com/api/v3/exchangeInfo"
    response = requests.get(url)
    data = response.json()

    symbols = [symbol['symbol'] for symbol in data['symbols']]
    return symbols


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
