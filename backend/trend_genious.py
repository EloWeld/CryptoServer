import ccxt
import pandas as pd
import time

# Функция для получения исторических данных с Binance


def get_ohlcv_data(symbol, timeframe, limit):
    exchange = ccxt.binance()
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

# Функция для определения тренда на основе скользящих средних и выявления точек смены тренда


def detect_trend_changes(df):
    # Вычисление скользящих средних
    df['SMA_7'] = df['close'].rolling(window=7).mean()
    df['SMA_30'] = df['close'].rolling(window=30).mean()

    trend_changes = []

    # Проход по данным для выявления точек смены тренда
    for i in range(1, len(df)):
        previous_sma_7 = df['SMA_7'].iloc[i-1]
        previous_sma_30 = df['SMA_30'].iloc[i-1]
        current_sma_7 = df['SMA_7'].iloc[i]
        current_sma_30 = df['SMA_30'].iloc[i]

        if pd.notna(previous_sma_7) and pd.notna(previous_sma_30) and pd.notna(current_sma_7) and pd.notna(current_sma_30):
            if previous_sma_7 <= previous_sma_30 and current_sma_7 > current_sma_30:
                # Смена тренда на восходящий
                trend_changes.append([df.index[i], 'BULL'])
            elif previous_sma_7 >= previous_sma_30 and current_sma_7 < current_sma_30:
                # Смена тренда на нисходящий
                trend_changes.append([df.index[i], 'BEAR'])

    return trend_changes


def get_trend_changes(symbol):
    symbol = symbol
    df = get_ohlcv_data(symbol, "1m", 300)
    trend_changes = detect_trend_changes(df)
    return trend_changes


if __name__ == "__main__":
    tc = get_trend_changes("BTCUSDT")

    for change in tc:
        print(f"Timestamp: {change[0]}, Trend: {change[1]}")
