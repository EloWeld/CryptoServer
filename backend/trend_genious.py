import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta

# Пример данных

# Генерация данных
date_rng = pd.date_range(start='2023-01-01', end='2023-01-31', freq='T')
price_data = np.random.normal(loc=30000, scale=500, size=len(date_rng))

# Создание DataFrame
df = pd.DataFrame(date_rng, columns=['timestamp'])
df['price'] = price_data

# Индикатор MACD
df['MACD'] = ta.trend.macd(df['price'])
df['Signal_Line'] = ta.trend.macd_signal(df['price'])
df['MACD_Hist'] = ta.trend.macd_diff(df['price'])

# Индикатор LongShort (для примера используем простой подход)
df['LongShort'] = np.where(df['price'] > df['price'].shift(1), 1, -1)  # Простое направление цены

# Генерация сигналов на основе пересечения индикаторов
def generate_signals(df):
    signals = []
    for i in range(1, len(df)):
        if df['MACD'][i] > df['Signal_Line'][i] and df['LongShort'][i] == 1:
            signals.append((df['timestamp'][i], 'Buy'))
        elif df['MACD'][i] < df['Signal_Line'][i] and df['LongShort'][i] == -1:
            signals.append((df['timestamp'][i], 'Sell'))
    return signals

signals = generate_signals(df)
for signal in signals:
    print(f"Timestamp: {signal[0]}, Signal: {signal[1]}")

import matplotlib.pyplot as plt

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