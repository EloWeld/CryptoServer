import json
import requests


symbols = ["BTCUSDT", "ETHUSDT"]
url = "https://fapi.binance.com/futures/data/openInterestHist"
params = {
        'symbol': 'BTCUSDT',
        'period': '1m'
    }

response = requests.get(url, params=params)
data = response.json()
print(data)