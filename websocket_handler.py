import json
import time
import ccxt
from pybit.unified_trading import WebSocket
from time import sleep, time
from collections import defaultdict
import threading

VOLUME_SPIKES_FILE = 'volume_spikes.json'
MONITORED_PAIRS = []
VOLUME_SPIKES = []
CANDLE_DATA = defaultdict(lambda: {'volume': 0, 'open_interest': 0, 'cvd': 0})
PREV_CANDLE_DATA = defaultdict(lambda: {'volume': 0, 'open_interest': 0, 'cvd': 0})
THREADS = []

def save_volume_spikes(spikes):
    with open(VOLUME_SPIKES_FILE, 'w') as f:
        json.dump(spikes, f, indent=4)

def load_volume_spikes():
    global VOLUME_SPIKES
    try:
        with open(VOLUME_SPIKES_FILE, 'r') as f:
            VOLUME_SPIKES = json.load(f)
    except FileNotFoundError:
        VOLUME_SPIKES = []

def handle_message(message):
    global VOLUME_SPIKES, CANDLE_DATA, PREV_CANDLE_DATA
    data = message.get("data", [])[0]
    pair = message.get("topic", "").split('.')[-1]
    curr_time = int(time())

    CANDLE_DATA[pair]['volume'] += float(data["volume"])
    CANDLE_DATA[pair]['open_interest'] += float(data.get("open_interest", 0))
    CANDLE_DATA[pair]['cvd'] += float(data.get("cvd", 0))

    if curr_time - CANDLE_DATA[pair].get('start_time', 0) >= 300:
        if CANDLE_DATA[pair]['volume'] >= 5 * PREV_CANDLE_DATA[pair]['volume']:
            VOLUME_SPIKES.append({
                'pair': pair,
                'prev_volume': PREV_CANDLE_DATA[pair]['volume'],
                'curr_volume': CANDLE_DATA[pair]['volume'],
                'time': curr_time
            })
            save_volume_spikes(VOLUME_SPIKES)
        
        PREV_CANDLE_DATA[pair] = CANDLE_DATA[pair]
        CANDLE_DATA[pair] = {'volume': 0, 'open_interest': 0, 'cvd': 0, 'start_time': curr_time}
    else:
        if 'start_time' not in CANDLE_DATA[pair]:
            CANDLE_DATA[pair]['start_time'] = curr_time

def subscribe_to_tickers(ws: WebSocket, pairs):
    for pair in pairs:
        try:
            ws.kline_stream(
                interval=5,
                symbol=pair,
                callback=handle_message
            )
        except Exception as e:
            print(f"Couldn't subscribe to topic. Error: {e}, topic: kline.5.{pair}")

def start_ws(pairs):
    while True:
        try:
            ws = WebSocket(
                testnet=True,
                channel_type="linear",
            )
            subscribe_to_tickers(ws, pairs)
            while True:
                sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            sleep(30)

def main():
    load_volume_spikes()
    exchange = ccxt.bybit()
    markets = exchange.load_markets()
    all_pairs = [symbol.replace('/', '') for symbol in markets if symbol.endswith('/USDT') and markets[symbol]['type'] == 'spot']
    valid_pairs = [pair for pair in all_pairs if pair not in ["TRIBEUSDT", "LUNCUSDT"]]

    for i in range(0, len(valid_pairs), 20):
        pairs_chunk = valid_pairs[i:i+20]
        print(f"Sent to subscribing pairs: {pairs_chunk}")
        thread = threading.Thread(target=start_ws, args=(pairs_chunk,))
        thread.start()
        THREADS.append(thread)

    for thread in THREADS:
        thread.join()

if __name__ == "__main__":
    main()
