import json
import traceback
import websocket
import threading
import pandas as pd
import time
import datetime
import requests
import loguru
import ccxt

from config import *
from tg_utils import spam_all
binance = ccxt.binance()

# Параметры для вывода сообщений в консоль
settings = {}

# Глобальный словарь для хранения истории цен
price_history = {}
spot_pairs = []
futures_pairs = []
lock = threading.Lock()


def send_webhook(setts, symbol, data, minute):
    url = setts['pump_webhook' if data['type'] == 'pump' else 'dump_webhook']
    data_template: str = setts['pump_data' if data['type'] == 'pump' else 'dump_data']
    data = data_template.replace('{{ticker}}', symbol)
    try:
        r = requests.post(url, headers={'Content-Type': "application/json"}, data=data)
        if r.status_code != 200:
            add_journal({"type": "error", "message": r.text,
                        "symbol": symbol, "created_at": minute})
    except Exception as e:
        add_journal({"type": "error", "message": str(
            e), "symbol": symbol, "created_at": minute})


def reload_settings():
    global settings
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        settings = json.load(f)


def add_journal(data):
    global settings
    log_file = CHANGES_LOG_FILE
    max_lines = 2000

    # Чтение существующего журнала
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Проверка на дублирование
    nowd = datetime.datetime.now()
    now = (int(nowd.timestamp()) // 60) * 60
    log_entries = []
    for line in lines:
        try:
            log_entry = json.loads(line)
        except Exception as e:
            continue
        log_entries.append(log_entry)
        if ('created_at' not in log_entry) or ('symbol' not in log_entry):
            continue
        log_time = datetime.datetime.strptime(log_entry["created_at"], "%Y-%m-%d %H:%M:%S")
        if log_entry["symbol"] == data["symbol"] and log_entry["type"] == data["type"] and datetime.datetime.now() - log_time < datetime.timedelta(minutes=settings['check_per_minutes']):
            return  # Запись уже существует, не добавляем дубликат

    # Добавление новой записи
    lines.append(json.dumps(data, ensure_ascii=False, default=str) + "\n")
    if data['type'] != "error":
        send_webhook(settings, data['symbol'], data, now)

    if data['type'] == "pump":
        spam_all(f"<b>🟢 Новый ПАМП!</b>\n"
                 f"🪙 Монета: <code>{data['symbol']}</code> <a href='https://www.coinglass.com/tv/Binance_{data['symbol']}'>ССЫЛКА</a>\n"
                 f"🎯 Биржа/Мод: <code>{data['exchange']}</code>\n"
                 f"📈 Изменение: <code>{data['change_amount']}</code> за <code>{data['interval']}</code> минут(-ы)\n"
                 f"🌐 Сайт: {settings['domain']}\n"
                 f"📣 Сигналов за сутки: {len([x for x in log_entries if datetime.datetime.strptime(x['created_at'], '%Y-%m-%d %H:%M:%S') > datetime.datetime(nowd.year, nowd.month, nowd.day)])}")
    elif data['type'] == "dump":
        spam_all(f"<b>🔴 Новый ДАМП!</b>\n"
                 f"🪙 Монета: <code>{data['symbol']}</code> <a href='https://www.coinglass.com/tv/Binance_{data['symbol']}'>ССЫЛКА</a>\n"
                 f"🎯 Биржа/Мод: <code>{data['exchange']}</code>\n"
                 f"📉 Изменение: <code>-{data['change_amount']}</code> за <code>{data['interval']}</code> минут(-ы)\n"
                 f"🌐 Сайт: {settings['domain']}\n"
                 f"📣 Сигналов за сутки: {len([x for x in log_entries if datetime.datetime.strptime(x['created_at'], '%Y-%m-%d %H:%M:%S') > datetime.datetime(nowd.year, nowd.month, nowd.day)])}")
    else:
        spam_all(f"<b>⚠️ Странное поведение!</b>\n"
                 f"Данные: <code>{data}</code>")

    # Оставляем только последние 2000 строк
    if len(lines) > max_lines:
        lines = lines[-max_lines:]

    # Запись обновленного журнала
    with open(log_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def update_price(message):
    global price_history, settings, spot_pairs, futures_pairs

    symbol = message['symbol']
    price = message['price']
    curr_minute = (int(datetime.datetime.now().timestamp()) // 60) * 60

    with lock:
        MAX_MINUTES = settings['max_save_minutes']
        N1 = settings['check_per_minutes']
        N2 = settings['check_per_minutes_mode_2']
        C1 = settings['price_change_percent']
        C2 = settings.get('price_change_trigger_percent', 0)
        COI = settings.get('oi_change_percent', 0)
        CCVD = settings.get('cvd_change_percent', 0)
        CVVC = settings.get('v_volumes_change_percent', 0)

        if symbol not in price_history:
            price_history[symbol] = [(curr_minute, price)]
        else:
            if price_history[symbol][-1][0] != curr_minute:
                price_history[symbol].append((curr_minute, price))
                if len(price_history[symbol]) > MAX_MINUTES:
                    price_history[symbol].pop(0)
            price_history[symbol][-1] = (curr_minute, price)

        def calculate_changes(prices, interval):
            old_price = prices[-(interval+1)][1]
            if settings['use_wicks']:
                min_price = min(x[1] for x in prices[-(interval+1):-1])
                max_price = max(x[1] for x in prices[-(interval+1):-1])
            else:
                min_price, max_price = old_price, old_price
            current_price = prices[-1][1]
            change_amount_pump = (current_price - min_price) / min_price * 100
            change_amount_dump = (max_price - current_price) / max_price * 100
            return change_amount_pump, change_amount_dump, min_price, max_price

        def log_and_journal(symbol, change_amount, change_type, mode, min_price, max_price, interval, current_price):
            loguru.logger.info(f"{symbol} price {change_type.upper()} by {change_amount:.2f}% over the last {interval} minutes; Datetime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            s_data = {
                "exchange": "binance" if mode == "price" else "binance_smooth",
                "symbol": symbol,
                "type": change_type,
                "mode": mode,
                "change_amount": f"{change_amount:.2f}%",
                "interval": interval,
                "old_price": min_price if change_type == "pump" else max_price,
                "curr_price": current_price,
                "created_at": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            try:
                add_journal(s_data)
            except Exception as e:
                loguru.logger.error(f"Error during journal append: {e}, {traceback.format_exc()}")

        if len(price_history[symbol]) > N1:
            change_amount_pump, change_amount_dump, min_price, max_price = calculate_changes(price_history[symbol], N1)
            if change_amount_pump >= C1 and settings['enable_pump']:
                log_and_journal(symbol, change_amount_pump, "pump", "price", min_price, max_price, N1, price_history[symbol][-1][1])
            if change_amount_dump >= C1 and settings['enable_dump']:
                log_and_journal(symbol, change_amount_dump, "dump", "price", min_price, max_price, N1, price_history[symbol][-1][1])

        if len(price_history[symbol]) > N2:
            change_amount_pump, change_amount_dump, min_price, max_price = calculate_changes(
                price_history[symbol], N2)
            if change_amount_pump >= C2 and settings['enable_pump']:
                oi = sorted(get_oi_candles(symbol, max(2, N2 // 5)), key=lambda x: x['timestamp'])
                oi_values = [float(x['sumOpenInterest']) for x in oi]
                oi_change = (oi_values[-1] - oi_values[0]) / oi_values[0] * 100
                if oi_change > COI:
                    cvd_change = get_cvd_change(symbol, N2+1)
                    if cvd_change > CCVD:
                        volumes_change = get_volumes_change(symbol, N2+1)
                        if volumes_change > CVVC:
                            log_and_journal(symbol, change_amount_pump, "pump", "smooth", min_price, max_price, N2, price_history[symbol][-1][1])
            if change_amount_dump >= C2 and settings['enable_dump']:
                oi = sorted(get_oi_candles(symbol, max(2, N2 // 5)), key=lambda x: x['timestamp'])
                oi_values = [float(x['sumOpenInterest']) for x in oi]
                oi_change = (oi_values[-1] - oi_values[0]) / oi_values[0] * 100
                if -oi_change > COI:
                    cvd_change = get_cvd_change(symbol, N2+1)
                    if -cvd_change > CCVD:
                        volumes_change = get_volumes_change(symbol, N2+1)
                        if -volumes_change > CVVC:
                            log_and_journal(symbol, change_amount_dump, "dump", "smooth", min_price, max_price, N2, price_history[symbol][-1][1])


def save_to_csv():
    global price_history
    global settings
    while True:
        time.sleep(20)  # 30 секунд
        with lock:
            reload_settings()
            if price_history:
                df_list = []
                for symbol, prices in price_history.items():
                    d = {'symbol': symbol}
                    for ts, price in prices:
                        d[str(ts)] = price
                    df_list.append(d)
                df = pd.DataFrame(df_list)
                df.to_csv(PRICE_SAVE_FILE, index=False)
                loguru.logger.info(f"Data saved at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


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


def tickers_receiver():
    while True:
        prices = get_spot_prices() if settings['use_spot'] else get_futures_prices()
        for price in prices:
            update_price(price)


if __name__ == "__main__":
    reload_settings()

    # Запуск нескольких подключений WebSocket
    threading.Thread(target=tickers_receiver).start()

    # Запуск сохранения данных
    threading.Thread(target=save_to_csv).start()
