from flask import Blueprint, request, jsonify, render_template, redirect, url_for
import time
import json
import os
import ccxt

main = Blueprint('main', __name__)

SETTINGS_FILE = 'settings.json'

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'w') as f:
            json.dump({"finandy_url": "URL_ТВОЕГО_ТЕРМИНАЛА", "domain": "https://ВАШ_ДОМЕН", "webhooks": [], "received_hooks": [], "blocked_hooks": 0}, f)
    with open(SETTINGS_FILE, 'r') as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

settings = load_settings()
last_hook_time = {}

@main.route('/')
def index():
    settings = load_settings()
    return render_template('index.html', settings=settings)

@main.route('/add', methods=['GET', 'POST'])
def add_webhook():
    if request.method == 'POST':
        webhook = request.form['webhook']
        delay = int(request.form['delay'])
        settings = load_settings()
        settings['webhooks'].append({"webhook": webhook, "delay": delay})
        save_settings(settings)
        return redirect('/')
    return render_template('add_webhook.html')

@main.route('/settings', methods=['GET', 'POST'])
def settings_page():
    if request.method == 'POST':
        finandy_url = request.form['finandy_url']
        domain = request.form['domain']
        settings = load_settings()
        settings['finandy_url'] = finandy_url
        settings['domain'] = domain
        save_settings(settings)
        return redirect('/')
    settings = load_settings()
    return render_template('settings.html', settings=settings)

@main.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    hook_id = data.get('id')
    current_time = time.time()
    
    settings = load_settings()
    delay = next((w['delay'] for w in settings['webhooks'] if w['webhook'] == hook_id), 30)

    if hook_id in last_hook_time:
        time_since_last_hook = current_time - last_hook_time[hook_id]
        if time_since_last_hook < delay:
            settings['blocked_hooks'] += 1
            save_settings(settings)
            return jsonify({"status": "ignored", "reason": f"Less than {delay} seconds since last hook"}), 200

    last_hook_time[hook_id] = current_time
    settings['received_hooks'].append({"hook_id": hook_id, "time": current_time})
    save_settings(settings)
    forward_hook(data, settings['finandy_url'])
    
    return jsonify({"status": "forwarded"}), 200

def forward_hook(data, finandy_url):
    import requests
    headers = {'Content-Type': 'application/json'}
    response = requests.post(finandy_url, json=data, headers=headers)
    return response

def get_bybit_tickers():
    exchange = ccxt.bybit()
    markets = exchange.load_markets()
    tickers = [symbol for symbol in markets if symbol.endswith('/USDT')]
    return tickers

def get_volume_spikes():
    exchange = ccxt.bybit()
    tickers = get_bybit_tickers()
    tickers = tickers
    spikes = []
    
    for i, ticker in enumerate(tickers):
        print(i)
        ohlcv = exchange.fetch_ohlcv(ticker, timeframe='5m', limit=2)
        if len(ohlcv) < 2:
            continue
        prev_candle, curr_candle = ohlcv[-2], ohlcv[-1]
        prev_volume, curr_volume = prev_candle[5], curr_candle[5]
        
        if curr_volume >= 5 * prev_volume and prev_volume != 0:
            spikes.append({
                'pair': ticker,
                'prev_volume': prev_volume,
                'curr_volume': curr_volume,
                'time': curr_candle[0]
            })
    
    return spikes

@main.route('/pairs')
def pairs():
    spikes = get_volume_spikes()
    return render_template('pairs.html', spikes=spikes)
