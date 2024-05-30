import json
import traceback
import websocket
import threading
import pandas as pd
import time
from datetime import datetime, timedelta
import requests
import loguru
import ccxt
binance = ccxt.binance()

SETTINGS_FILE = 'settings_new.json'
CHANGES_LOG_FILE = 'changes_log.txt'
PRICE_SAVE_FILE = 'binance_prices.csv'

# Параметры для вывода сообщений в консоль
settings = {}

# Глобальный словарь для хранения истории цен
price_history = {}
spot_pairs = []
futures_pairs = []
lock = threading.Lock()


def send_webhook(setts, symbol, data, minute):
    url = setts['pump_webhook' if data['type'] == 'pump' else 'dump_webhook']
    data_template = setts['pump_data' if data['type']
                          == 'pump' else 'dump_data']
    data = data_template.replace('{{ticker}}', symbol)
    try:
        r = requests.post(
            url, headers={'Content-Type': "application/json"}, data=data)
        if r.status_code != 200:
            add_journal({"type": "error", "message": r.text, "symbol": symbol, "created_at": minute})
    except Exception as e:
        add_journal({"type": "error", "message": str(e), "symbol": symbol, "created_at": minute})


def reload_settings():
    global settings
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        settings = json.load(f)


def add_journal(data):
    log_file = CHANGES_LOG_FILE
    max_lines = 2000

    # Чтение существующего журнала
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Проверка на дублирование
    now = (int(datetime.now().timestamp()) // 60) * 60
    for line in lines:
        try:
            log_entry = json.loads(line)
        except Exception as e:
            continue
        if ('created_at' not in log_entry) or ('symbol' not in log_entry):
            continue
        log_time = datetime.strptime(log_entry["created_at"], "%Y-%m-%d %H:%M:%S")
        if log_entry["symbol"] == data["symbol"] and log_entry["type"] == data["type"] and now - log_time < timedelta(minutes=settings['check_per_minutes']):
            return  # Запись уже существует, не добавляем дубликат

    # Добавление новой записи
    lines.append(json.dumps(data, ensure_ascii=False, default=str) + "\n")
    if data['type'] != "error":
        send_webhook(settings, data['symbol'], data, now)

    # Оставляем только последние 2000 строк
    if len(lines) > max_lines:
        lines = lines[-max_lines:]

    # Запись обновленного журнала
    with open(log_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def update_price(message):
    global price_history
    global settings
    global spot_pairs
    global futures_pairs

    symbol = message['symbol']
    price = message['price']
    curr_minute = (int(datetime.now().timestamp()) // 60) * 60
    # print(timestamp)
    # print(symbol,"-",price, timestamp)
    with lock:
        
        MAX_MINUTES = settings['max_save_minutes']
        N = settings['check_per_minutes']
        M = settings['min_change_percent']
        
        C2 = settings.get('min_change_percent_smooth', 0)
        COI = settings.get('min_oi_change', 0)
        CCVD = settings.get('min_cvd_change', 0)
        CVVC = settings.get('min_vert_vols_change', 0)
        
        
        if symbol not in price_history:
            # If no prices yet
            price_history[symbol] = []
            price_history[symbol].append((curr_minute, price))
        else:
            if price_history[symbol][-1][0] == curr_minute:
                # If we in current minute candle
                pass
            else:
                # If new candle started add open_time+open_price
                price_history[symbol].append((curr_minute, price))
                # Сохраняем только последние 20 минут
                if len(price_history[symbol]) > MAX_MINUTES:
                    price_history[symbol].pop(0)

        price_history[symbol][-1] = (curr_minute, price)

        # print(N, M, MAX_MINUTES)

        if len(price_history[symbol]) > N:
            old_price = price_history[symbol][-(N+1)][1]

            if settings['use_wicks']:
                min_price = min([x[1] for x in price_history[symbol][-(N+1):-1]])
                max_price = max([x[1] for x in price_history[symbol][-(N+1):-1]])
            else:
                min_price = old_price
                max_price = old_price
            
            current_price = price_history[symbol][-1][1]
            change_amount_pump = (float(current_price) - float(min_price)) / float(min_price) * 100
            change_amount_dump = (float(max_price) - float(current_price)) / float(max_price) * 100
            # print(change_amount_pump, change_amount_dump, M)
            # print(old_price, current_price, change_amount)
            # oi_candles_pump = True
            # oi_candles_dump = True
            # if min_oi_candls > 0:
            #     oi_candles = get_oi_candles(symbol, min_oi_candls)
            #     oi_candles_pump = all([oi_candles[i] > oi_candles[i] for i in range(len(oi_candles) - 1)])
            #     oi_candles_dump = all([oi_candles[i] < oi_candles[i] for i in range(len(oi_candles) - 1)])
                
            if change_amount_pump >= M and settings['enable_pump']:
                loguru.logger.info(f"{symbol} price PUMPED by {change_amount_pump:.2f}% over the last {N} minutes; Datetime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                s_data = {"exchange": "binance", "symbol": symbol, "type": "pump", "mode": "price", "change_amount": f"{change_amount_pump:.2f}%",
                          "interval": N, "old_price": min_price, "curr_price": current_price, "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                try:
                    add_journal(s_data)
                except Exception as e:
                    loguru.logger.error(f"Error during journal append: {e}, {traceback.format_exc()}")

            if change_amount_dump >= M and settings['enable_pump']:
                loguru.logger.info(f"{symbol} price DUMPED by {change_amount_dump:.2f}% over the last {N} minutes Datetime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                s_data = {"exchange": "binance", "symbol": symbol, "type": "dump", "mode": "price", "change_amount": f"{change_amount_dump:.2f}%",
                          "interval": N, "old_price": max_price, "curr_price": current_price, "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                try:
                    add_journal(s_data)
                except Exception as e:
                    loguru.logger.error(f"Error during journal append: {e}, {traceback.format_exc()}")


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
                loguru.logger.info(f"Data saved at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def get_oi_candles(symbol, period):
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
