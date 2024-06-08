# app/routes/dashboard.py
from copy import deepcopy
import traceback
from flask import Blueprint, Flask, current_app, jsonify, request
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
import jwt
from app import socketio
import threading
import time
import loguru

from app.models import ChangesLog, FuturesPrice, ParsingProcess, Settings, SpotPrice, User, db
from app.utils import *
from sqlalchemy.orm import scoped_session, sessionmaker

processes_bp = Blueprint('processes', __name__)

process_threads = {}
process_running = {}
price_history = {}
lock = threading.Lock()


def save_prices_to_db(app):

    with app.app_context():
        engine = db.get_engine()
        Session = scoped_session(sessionmaker(bind=engine))
        session = Session()
        while True:
            spot_prices = get_spot_prices()
            futures_prices = get_futures_prices()

            session.query(SpotPrice).delete(synchronize_session='evaluate')
            session.query(FuturesPrice).delete(synchronize_session='evaluate')
            for price in spot_prices:
                session.add(SpotPrice(symbol=price['symbol'], price=price['price']))
            for price in futures_prices:
                session.add(FuturesPrice(symbol=price['symbol'], price=price['price']))

            with lock:
                session.commit()
            time.sleep(2)


def start_price_saving_thread():
    app = current_app._get_current_object()
    price_thread = threading.Thread(target=save_prices_to_db, args=(app,))
    price_thread.start()


def start_user_processes():
    app = current_app._get_current_object()
    running_processes = db.session.query(ParsingProcess).filter(ParsingProcess.status == "active")
    for running_process in running_processes:
        price_thread = threading.Thread(target=process_function, args=(app, running_process.user_id))
        price_thread.start()


def send_webhook(settings: Settings, symbol, data, minute, user_id):
    if data['exchange'] == "rapid":
        url = settings.rapid_pump_webhook if data['type'] == 'pump' else settings.rapid_dump_webhook
        data_template: str = settings.rapid_pump_data if data['type'] == 'pump' else settings.rapid_dump_data
    elif data['exchange'] == "smooth":
        url = settings.smooth_pump_webhook if data['type'] == 'pump' else settings.smooth_dump_webhook
        data_template: str = settings.smooth_pump_data if data['type'] == 'pump' else settings.smooth_dump_data

    data = data_template.replace('{{ticker}}', symbol)
    try:
        r = requests.post(url, headers={'Content-Type': "application/json"}, data=data)
        if r.status_code != 200:
            add_journal({"type": "error", "message": r.text,
                        "symbol": symbol, "created_at": datetime.datetime.now()}, settings, user_id)
    except Exception as e:
        add_journal({"type": "error", "message": str(
            e), "symbol": symbol, "created_at": datetime.datetime.now()}, settings, user_id)


def add_journal(data: dict, settings: Settings, user_id: str | int):
    loguru.logger.info(str(data) + f" {user_id}")
    # Чтение существующего журнала
    change_log: list[ChangesLog] = ChangesLog.query.filter(ChangesLog.user_id == user_id)
    # Проверка на дублирование
    nowd = datetime.datetime.now()
    now = (int(nowd.timestamp()) // 60) * 60
    for log_entry in change_log:
        delay = 3
        if 'exchange' in data:
            if data['exchange'] == "rapid":
                delay = settings.rapid_delay
            elif data['exchange'] == "smooth":
                delay = settings.rapid_delay

        if log_entry.symbol == data["symbol"] and log_entry.type == data["type"] and datetime.datetime.now() - log_entry.created_at < datetime.timedelta(minutes=delay):
            return  # Запись уже существует, не добавляем дубликат

    if data['type'] != "error":
        send_webhook(settings, data['symbol'], data, now, user_id)

    if settings.tg_id and settings.tg_id > 1000:
        if data['type'] == "pump":
            send_tg_message(settings.tg_id, f"<b>🟢 Новый ПАМП!</b>\n"
                            f"🪙 Монета: <code>{data['symbol']}</code> <a href='https://www.coinglass.com/tv/Binance_{data['symbol']}'>ССЫЛКА</a>\n"
                            f"🎯 Режим: <code>{data['exchange']}</code>\n"
                            f"📈 Изменение: <code>{data['change_amount']}</code> за <code>{data['interval']}</code> минут(-ы)\n"
                            f"🌐 Сайт: {settings.domain}\n"
                            f"📣 Сигналов за сутки: {len([x for x in change_log if x.created_at > datetime.datetime(nowd.year, nowd.month, nowd.day)])}")

        elif data['type'] == "dump":
            send_tg_message(settings.tg_id, f"<b>🔴 Новый ДАМП!</b>\n"
                            f"🪙 Монета: <code>{data['symbol']}</code> <a href='https://www.coinglass.com/tv/Binance_{data['symbol']}'>ССЫЛКА</a>\n"
                            f"🎯 Режим: <code>{data['exchange']}</code>\n"
                            f"📉 Изменение: <code>-{data['change_amount']}</code> за <code>{data['interval']}</code> минут(-ы)\n"
                            f"🌐 Сайт: {settings.domain}\n"
                            f"📣 Сигналов за сутки: {len([x for x in change_log if x.created_at > datetime.datetime(nowd.year, nowd.month, nowd.day)])}")
        else:
            send_tg_message(settings.tg_id, f"<b>⚠️ Странное поведение!</b>\n"
                            f"Данные: <code>{data}</code>")

    db.session.add(ChangesLog(user_id=user_id,
                              exchange=data.get('exchange', None),
                              symbol=data.get('symbol', None),
                              type=data.get('type', None),
                              mode=data.get('mode', None),
                              change_amount=data.get('change_amount', None),
                              interval=data.get('interval', None),
                              created_at=datetime.datetime.now(),
                              old_price=data.get('old_price', None), curr_price=data.get('curr_price', None)))
    db.session.commit()


def update_price(settings: Settings, message: FuturesPrice, username: str | int):
    global price_history
    symbol = message.symbol
    price = float(message.price)
    curr_minute = (int(time.time()) // 60)

    with lock:
        MAX_MINUTES = settings.max_save_minutes
        RAPID_CHECK_MINUTES = settings.check_per_minutes_rapid
        SMOOTH_CHECK_MINUTES = settings.check_per_minutes_smooth
        RAPID_PRICE_CHANGE = settings.price_change_percent
        SMOOTH_PRICE_CHANGE = settings.price_change_trigger_percent
        COI = settings.oi_change_percent
        CCVD = settings.cvd_change_percent
        CVVC = settings.v_volumes_change_percent

        if settings.user_id not in price_history:
            price_history[settings.user_id] = {}

        if symbol not in price_history[settings.user_id]:
            price_history[settings.user_id][symbol] = [(curr_minute, price)]
        else:
            if price_history[settings.user_id][symbol][-1][0] != curr_minute:
                price_history[settings.user_id][symbol].append((curr_minute, price))
                if len(price_history[settings.user_id][symbol]) > MAX_MINUTES:
                    price_history[settings.user_id][symbol].pop(0)
            price_history[settings.user_id][symbol][-1] = (curr_minute, price)

        def calculate_changes(prices, interval):
            old_price = prices[-(interval+1)][1]
            if settings.use_wicks:
                min_price = min(x[1] for x in prices[-(interval+1):-1])
                max_price = max(x[1] for x in prices[-(interval+1):-1])
            else:
                min_price, max_price = old_price, old_price
            current_price = prices[-1][1]
            change_amount_pump = (current_price - min_price) / min_price * 100
            change_amount_dump = (max_price - current_price) / max_price * 100
            return change_amount_pump, change_amount_dump, min_price, max_price

        def log_and_journal(symbol, change_amount, change_type, mode, min_price, max_price, interval, current_price):
            loguru.logger.success(f"{symbol} price {change_type.upper()} by {change_amount:.2f}% over the last {interval} minutes; Datetime: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            s_data = {
                "exchange": "rapid" if mode == "price" else "smooth",
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
                add_journal(s_data, settings, username)
            except Exception as e:
                err_msg = f"Error during journal append: {e}, {traceback.format_exc()}"
                loguru.logger.error(err_msg)
                socketio.emit('log', {'data': err_msg}, room=username)

        if len(price_history[settings.user_id][symbol]) > RAPID_CHECK_MINUTES:
            change_amount_pump, change_amount_dump, min_price, max_price = calculate_changes(price_history[settings.user_id][symbol], RAPID_CHECK_MINUTES)
            if change_amount_pump >= RAPID_PRICE_CHANGE and settings.rapid_enable_pump:
                log_and_journal(symbol, change_amount_pump, "pump", "price", min_price, max_price, RAPID_CHECK_MINUTES, price_history[settings.user_id][symbol][-1][1])
            if change_amount_dump >= RAPID_PRICE_CHANGE and settings.rapid_enable_dump:
                log_and_journal(symbol, change_amount_dump, "dump", "price", min_price, max_price, RAPID_CHECK_MINUTES, price_history[settings.user_id][symbol][-1][1])

        if len(price_history[settings.user_id][symbol]) > SMOOTH_CHECK_MINUTES:
            change_amount_pump, change_amount_dump, min_price, max_price = calculate_changes(
                price_history[settings.user_id][symbol], SMOOTH_CHECK_MINUTES)
            if change_amount_pump >= SMOOTH_PRICE_CHANGE and settings.smooth_enable_pump:
                oi = sorted(get_oi_candles(symbol, max(2, SMOOTH_CHECK_MINUTES // 5)), key=lambda x: x['timestamp'])
                oi_values = [float(x['sumOpenInterest']) for x in oi]
                oi_change = (oi_values[-1] - oi_values[0]) / oi_values[0] * 100
                if oi_change > COI:
                    cvd_change = get_cvd_change(symbol, SMOOTH_CHECK_MINUTES+1)
                    if cvd_change > CCVD:
                        volumes_change = get_volumes_change(symbol, SMOOTH_CHECK_MINUTES+1)
                        if volumes_change > CVVC:
                            log_and_journal(symbol, change_amount_pump, "pump", "smooth", min_price, max_price, SMOOTH_CHECK_MINUTES, price_history[settings.user_id][symbol][-1][1])
            if change_amount_dump >= SMOOTH_PRICE_CHANGE and settings.smooth_enable_dump:
                oi = sorted(get_oi_candles(symbol, max(2, SMOOTH_CHECK_MINUTES // 5)), key=lambda x: x['timestamp'])
                oi_values = [float(x['sumOpenInterest']) for x in oi]
                oi_change = (oi_values[-1] - oi_values[0]) / oi_values[0] * 100
                if -oi_change > COI:
                    cvd_change = get_cvd_change(symbol, SMOOTH_CHECK_MINUTES+1)
                    if -cvd_change > CCVD:
                        volumes_change = get_volumes_change(symbol, SMOOTH_CHECK_MINUTES+1)
                        if -volumes_change > CVVC:
                            log_and_journal(symbol, change_amount_dump, "dump", "smooth", min_price, max_price, SMOOTH_CHECK_MINUTES, price_history[settings.user_id][symbol][-1][1])


def process_function(app: Flask, user_id):
    with app.app_context():
        engine = db.get_engine()
        Session = scoped_session(sessionmaker(bind=engine))
        session = Session()

        try:
            user: User = session.query(User).get(user_id)
            loguru.logger.info(f"Process started for user {user_id} {user.username}")
            socketio.emit('log', {'data': f'Process started for user {user_id}.'}, room=user_id)
            process = session.query(ParsingProcess).filter(ParsingProcess.user_id == user.id, ParsingProcess.status == "active").first()
            while process is not None:
                process = session.query(ParsingProcess).filter(ParsingProcess.user_id == user.id, ParsingProcess.status == "active").first()
                us: Settings = session.query(Settings).filter(Settings.user_id == user.id).first()
                if us.use_spot:
                    prices = session.query(SpotPrice).all()
                else:
                    prices = session.query(FuturesPrice).all()
                prices_copy = deepcopy(prices)  # Создание копии объекта
                for price in prices_copy:
                    try:
                        update_price(us, price, user_id)
                    except Exception as e:
                        err_msg = f"Error in cycle {e} {traceback.format_exc()}"
                        loguru.logger.error(err_msg)
                        socketio.emit('log', {'data': err_msg}, room=user_id)

                time.sleep(0.5)
            loguru.logger.info(f"Process has stopped for user {user_id} {user.username}")
            socketio.emit('log', {'data': f'Process has stopped for user {user_id} {user.username}.'}, room=user_id)
            process_running[user_id] = False
            if user_id in process_threads:
                del process_threads[user_id]
        finally:
            session.close()


@processes_bp.route('/api/start_process', methods=['POST'])
@login_required
def start_process():
    user_id = current_user.id
    running_process = db.session.query(ParsingProcess).filter(ParsingProcess.user_id == user_id, ParsingProcess.status == "active").first()
    if running_process is not None:
        return jsonify({'status': 'Process already running'})

    if running_process is None:
        db.session.add(ParsingProcess(user_id=user_id, status="active"))
        db.session.commit()
        app = current_app._get_current_object()  # Wattafock? Works! Magick!
        process_thread = threading.Thread(target=process_function, args=(app, user_id,))
        process_threads[user_id] = process_thread
        process_thread.start()
        return jsonify({'status': 'Process started'})


@processes_bp.route('/api/get_process_status', methods=['GET'])
@login_required
def get_process_status():
    user_id = current_user.id
    running_process = db.session.query(ParsingProcess).filter(ParsingProcess.user_id == user_id, ParsingProcess.status == "active").first()
    return jsonify({"is_running": running_process is not None}), 200


@processes_bp.route('/api/stop_process', methods=['POST'])
@login_required
def stop_process():
    user_id = current_user.id
    running_process = db.session.query(ParsingProcess).filter(ParsingProcess.user_id == user_id, ParsingProcess.status == "active").first()
    if running_process is None:
        return jsonify({"status": "Process is not running now"})

    running_process.status = "finished"
    running_process.ended_at = datetime.datetime.now()

    db.session.commit()

    if user_id in process_threads:
        process_threads[user_id].join()
        try:
            del process_threads[user_id]
        except Exception as e:
            loguru.logger.error(str(e))
    return jsonify({'status': 'Process stopped'})


@socketio.on('connect')
def connect(auth: dict):
    token = auth.get('token', None) if auth else None
    if not token:
        loguru.logger.error(f"Disconnect, no token {auth}")

        disconnect()
        return False
    try:
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        user = User.query.get(data['user_id'])
        if user:
            loguru.logger.info(f"Connect to server!")
            # Присоединение пользователя к комнате
            join_room(user.id)
            emit('log', {'data': f'Connected to server as {user.username}'}, room=user.id)
        else:
            disconnect()
            return False
    except Exception as e:
        loguru.logger.error(f"Connection rejected: {e}")
        disconnect()
        return False


@socketio.on('disconnect')
def disconnect():
    if current_user.is_authenticated:
        leave_room(current_user.id)
