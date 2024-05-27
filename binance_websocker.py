import json
import traceback
import websocket
import threading
import pandas as pd
import time
from datetime import datetime, timedelta
import requests
import loguru
# Параметры для вывода сообщений в консоль
settings = {}

# Глобальный словарь для хранения истории цен
price_history = {}
lock = threading.Lock()

def send_webhook(setts, symbol, data):
    url = setts['pump_webhook' if data['type'] == 'pump' else 'dump_webhook']
    data_template = setts['pump_data' if data['type'] == 'pump' else 'dump_data']
    data = data_template.replace('{{ticker}}', symbol)
    try:
        r = requests.post(url, headers={'Content-Type': "application/json"}, data=data)
        if r.status_code != 200:
            add_journal({"type": "error", "message": r.text})
    except Exception as e:
        add_journal({"type": "error", "message": str(e)})

def reload_settings():
    global settings
    with open('settings.json', 'r', encoding='utf-8') as f:
        settings = json.load(f)

def add_journal(data):
    log_file = "changes_log.txt"
    max_lines = 2000

    # Чтение существующего журнала
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Проверка на дублирование
    now = datetime.now()
    for line in lines:
        log_entry = json.loads(line)
        log_time = datetime.strptime(log_entry["created_at"], "%Y-%m-%d %H:%M:%S")
        if log_entry["symbol"] == data["symbol"] and log_entry["type"] == data["type"] and now - log_time < timedelta(minutes=settings['check_per_minutes']):
            return  # Запись уже существует, не добавляем дубликат

    # Добавление новой записи
    lines.append(json.dumps(data, ensure_ascii=False, default=str) + "\n")

    # Оставляем только последние 2000 строк
    if len(lines) > max_lines:
        lines = lines[-max_lines:]

    # Запись обновленного журнала
    with open(log_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def on_message(ws, message):
    global price_history
    global settings

    data = json.loads(message)
    if 's' not in data:
        loguru.logger.info("D_message")
        return
    symbol = data['s']
    price = data['c']
    timestamp = data['E'] // 1000 // 60
    # print(timestamp)
    # print(symbol,"-",price, timestamp)
    with lock:
        if symbol not in price_history:
            price_history[symbol] = []
            price_history[symbol].append((timestamp, price))
        else:
            if price_history[symbol][-1][0] == timestamp:
                return
            else:
                price_history[symbol].append((timestamp, price))
        price_history[symbol][-1] = (timestamp, price)
        MAX_MINUTES = settings['max_save_minutes']
        # Сохраняем только последние 20 минут
        if len(price_history[symbol]) > MAX_MINUTES:
            price_history[symbol].pop(0)

        N = settings['check_per_minutes']
        M = settings['min_change_percent']
        # print(N, M, MAX_MINUTES)

        if len(price_history[symbol]) > N:
            old_price = price_history[symbol][-(N+1)][1]
            current_price = price_history[symbol][-1][1]
            change_amount = (float(current_price) - float(old_price)) / float(old_price) * 100
            # print(old_price, current_price, change_amount)
            if change_amount >= M:
                loguru.logger.info(f"{symbol} price PUMPED by {change_amount:.2f}% over the last {N} minutes; Datetime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                s_data = {"exchange": "binance", "symbol": symbol, "type": "pump", "mode": "price", "change_amount": f"{change_amount:.2f}%", "interval": N, "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                try:
                    add_journal(s_data)
                    send_webhook(settings, symbol, s_data)
                except Exception as e:
                    loguru.logger.error(f"Error during journal append: {e}, {traceback.format_exc()}")

            if change_amount * -1 >= M:
                loguru.logger.info(f"{symbol} price DUMPED by {change_amount:.2f}% over the last {N} minutes Datetime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                s_data = {"exchange": "binance", "symbol": symbol, "type": "dump", "mode": "price", "change_amount": f"{change_amount:.2f}%", "interval": N, "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                try:
                    add_journal(s_data)
                    send_webhook(settings, symbol, s_data)
                except Exception as e:
                    loguru.logger.error(f"Error during journal append: {e}, {traceback.format_exc()}")

def on_error(ws, error):
    loguru.logger.error(f"Error: {error}, {traceback.format_exc()}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def on_open(ws, pairs):
    params = [f"{pair.lower()}@ticker" for pair in pairs]
    ws.send(json.dumps({
        "method": "SUBSCRIBE",
        "params": params,
        "id": 1
    }))
    print(f"Subscribed to: {params}")

def save_to_csv():
    global price_history
    global settings
    while True:
        time.sleep(30)  # 30 секунд
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
                df.to_csv(f'binance_prices.csv', index=False)
                loguru.logger.info(f"Data saved at {ts}")

def start_websocket(pairs):
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp("wss://stream.binance.com:9443/ws",
                                on_open=lambda ws: on_open(ws, pairs),
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()

def get_usdt_pairs():
    url = 'https://api.binance.com/api/v3/ticker/price'
    response = requests.get(url).json()
    usdt_pairs = [item['symbol'] for item in response if item['symbol'].endswith('USDT')]
    return usdt_pairs

if __name__ == "__main__":
    usdt_pairs = get_usdt_pairs()
    num_pairs = len(usdt_pairs)
    max_pairs_per_ws = 210
    reload_settings()

    # Запуск нескольких подключений WebSocket
    for i in range(0, num_pairs, max_pairs_per_ws):
        pairs = usdt_pairs[i:i + max_pairs_per_ws]
        loguru.logger.info(f"{i}, {i + max_pairs_per_ws}, {len(pairs)}")
        threading.Thread(target=start_websocket, args=(pairs,)).start()

    # Запуск сохранения данных
    threading.Thread(target=save_to_csv).start()
