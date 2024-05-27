import requests
import pandas as pd
import concurrent.futures

def fetch_klines(symbol, interval='5m', limit=2):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}'
    response = requests.get(url)
    return response.json()

def process_klines(symbol):
    data = fetch_klines(symbol)
    if len(data) < 2:
        return None
    
    latest = data[-1]
    prev = data[-2]
    
    processed_data = {
        'symbol': symbol,
        'open': latest[1],
        'close': latest[4],
        'high': latest[2],
        'low': latest[3],
        'volume': latest[5],
        'prev_open': prev[1],
        'prev_close': prev[4],
        'prev_high': prev[2],
        'prev_low': prev[3],
        'prev_volume': prev[5],
    }
    
    return processed_data

def get_usdt_pairs():
    url = 'https://api.binance.com/api/v3/ticker/price'
    response = requests.get(url).json()
    usdt_pairs = [item['symbol'] for item in response if item['symbol'].endswith('USDT')]
    return usdt_pairs

def save_to_csv(data, filename='binance_klines.csv'):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)

def main():
    usdt_pairs = get_usdt_pairs()
    processed_data = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_symbol = {executor.submit(process_klines, symbol): symbol for symbol in usdt_pairs}
        for future in concurrent.futures.as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                data = future.result()
                if data:
                    processed_data.append(data)
            except Exception as e:
                print(f"Exception for {symbol}: {e}")

    save_to_csv(processed_data)

if __name__ == "__main__":
    main()
