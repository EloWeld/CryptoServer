from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta

# Пример данных
data = [
    {"12310239": {"btcusdt": [(28678585, 0.004257), (28678586, 0.004255), (28678587, 0.004294), (28678588, 0.004296), (28678589, 0.004295), (28678590, 0.004324), (28678591, 0.004302), (28678592, 0.004299), (28678593, 0.004291), (28678594, 0.004288), (28678595, 0.004267), (28678596, 0.004263), (28678597, 0.004257), (28678598, 0.004254), (28678599, 0.004254), (28678600, 0.004245), (28678601, 0.004245), (28678602, 0.004234), (28678603, 0.004241), (28678604, 0.004241), (28678605, 0.004244), (28678606, 0.00425), (28678607, 0.004256), (28678608, 0.004257), (28678609, 0.004255), (28678610, 0.004237), (28678611, 0.004233), (28678612, 0.004241), (28678613, 0.004239), (28678614, 0.004244), (28678615, 0.004237), (28678616, 0.004244), (28678617, 0.004241), (28678618, 0.004241), (28678619, 0.004261), (28678620, 0.004299), (28678621, 0.004307), (28678622, 0.004301), (28678623, 0.004319), (28678624, 0.004333), (28678625, 0.004355), (28678626, 0.004307), (28678627, 0.004288), (28678628, 0.004285), (28678629, 0.004271), (28678630, 0.004274), (28678631, 0.004248), (28678632, 0.00425), (28678633, 0.004254), (28678634, 0.004256), (28678635, 0.004264), (28678636, 0.00425), (28678637, 0.004282), (28678638, 0.00427), (28678639, 0.004277), (28678640, 0.00429), (28678641, 0.004282), (28678642, 0.004274), (28678643, 0.00428), (28678644, 0.004361)]}},
]
# Преобразование данных в DataFrame
price_data = [
    {"timestamp": datetime.fromtimestamp(ts), "price": price}
    for d in data
    for user_id, info in d.items()
    for ts, price in info["btcusdt"]
]

df = pd.DataFrame(price_data)

# Индикатор MACD
df['MACD'] = ta.trend.macd(df['price'])
df['Signal_Line'] = ta.trend.macd_signal(df['price'])
df['MACD_Hist'] = ta.trend.macd_diff(df['price'])

# Индикатор LongShort (пример определения разрывов справедливой стоимости)
def calculate_longshort(df, atr_multiplier=0.25, lookback=10):
    df['ATR'] = ta.volatility.average_true_range(df['price'], df['price'], df['price'], window=lookback) * atr_multiplier
    df['FVG_Up'] = (df['price'] > df['price'].shift(2)) & (df['price'].shift(1) > df['price'].shift(2)) & (df['price'] - df['price'].shift(2) > df['ATR'])
    df['FVG_Down'] = (df['price'] < df['price'].shift(2)) & (df['price'].shift(1) < df['price'].shift(2)) & (df['price'].shift(2) - df['price'] > df['ATR'])
    return df

df = calculate_longshort(df)

# Генерация сигналов на основе пересечения индикаторов
def generate_signals(df):
    signals = []
    for i in range(1, len(df)):
        if df['MACD'][i] > df['Signal_Line'][i] and df['FVG_Up'][i]:
            signals.append((df['timestamp'][i], 'Buy'))
        elif df['MACD'][i] < df['Signal_Line'][i] and df['FVG_Down'][i]:
            signals.append((df['timestamp'][i], 'Sell'))
    return signals

signals = generate_signals(df)
for signal in signals:
    print(f"Timestamp: {signal[0]}, Signal: {signal[1]}")

# Отображение цен и индикаторов
plt.figure(figsize=(14, 10))

# Цена
plt.subplot(3, 1, 1)
plt.plot(df['timestamp'], df['price'], label='Price')
plt.title('Price and Signals')
plt.legend()

# Сигналы
buy_signals = [signal[0] for signal in signals if signal[1] == 'Buy']
sell_signals = [signal[0] for signal in signals if signal[1] == 'Sell']

plt.scatter(buy_signals, df[df['timestamp'].isin(buy_signals)]['price'], marker='^', color='g', label='Buy Signal')
plt.scatter(sell_signals, df[df['timestamp'].isin(sell_signals)]['price'], marker='v', color='r', label='Sell Signal')
plt.legend()

# MACD и Signal Line
plt.subplot(3, 1, 2)
plt.plot(df['timestamp'], df['MACD'], label='MACD')
plt.plot(df['timestamp'], df['Signal_Line'], label='Signal Line')
plt.title('MACD and Signal Line')
plt.legend()

# Гистограмма MACD
plt.subplot(3, 1, 3)
plt.bar(df['timestamp'], df['MACD_Hist'], label='MACD Histogram')
plt.title('MACD Histogram')
plt.legend()

plt.tight_layout()
plt.show()