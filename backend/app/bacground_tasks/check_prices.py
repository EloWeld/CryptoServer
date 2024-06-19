import traceback
from app.bacground_tasks.base import lock, price_history, webhook_data
from app.bacground_tasks.logs_utils import add_journal, send_reverse_webhook
from app.bacground_tasks.base import connect_to_db
from app import socketio
from sqlalchemy import func, desc
from sqlalchemy.orm import aliased

import threading

from app.bacground_tasks.math_utils import generate_order_grid
from app.models import ChangesLog, FuturesPrice, ParsingProcess, Settings
from app.utils import datetime, get_cvd_change, get_oi_candles_minutes, get_volumes_change, loguru, time


def get_threshhold_price(settings: Settings, logged_type: str, logged_price):
    drop_percent = settings.reverse_last_order_dist
    if logged_type == "dump":
        # Attention! To make reversal position we need to loose our position on pump during drop_percent orders in grid
        # By default positive numbers in drop_percent will create descending grid and otherwise,
        # Negative number will create an ascending grid
        drop_percent *= 1
    grid = generate_order_grid(logged_price, settings.reverse_density, drop_percent, settings.reverse_full_orders_count)

    return grid[settings.reverse_orders_count]


def check_prices():
    session = connect_to_db()
    while True:
        with lock:
            subquery = session.query(ChangesLog.user_id, func.max(ChangesLog.created_at).label('max_created_at')
                                     ).join(ParsingProcess, ParsingProcess.user_id == ChangesLog.user_id).filter(ParsingProcess.status == "active").group_by(ChangesLog.user_id).subquery()

            # Алиас для ChangesLog, чтобы соединить с подзапросом
            cl_alias = aliased(ChangesLog)

            # Запрос для получения последних логов для каждого user_id
            lastlogs = session.query(cl_alias).join(subquery, (cl_alias.user_id == subquery.c.user_id) & (cl_alias.created_at == subquery.c.max_created_at)).order_by(desc(cl_alias.created_at))

            # Пример для получения результатов
            results = lastlogs.all()

            for log in results:
                if log.user_id not in price_history:
                    continue
                if log.symbol not in price_history[log.user_id]:
                    continue
                if len(price_history[log.user_id][log.symbol]) < 2:
                    continue
                settings: Settings = session.query(Settings).filter(Settings.user_id == log.user_id).first()
                # Filter too old logs
                if datetime.datetime.now() - log.created_at > datetime.timedelta(minutes=settings.max_save_minutes):
                    continue

                curr_user_prices = price_history[log.user_id][log.symbol]
                logged_price = log.curr_price
                curr_price = curr_user_prices[-1][-1]
                threshold_price = get_threshhold_price(settings, log.type, logged_price)

                # Creates reversal position of pump and otherwise
                if log.type == 'pump' and curr_price <= threshold_price:
                    # Filter enable flags
                    if log.exchange == "rapid" and settings.reverse_rapid_enable_pump:
                        continue
                    if log.exchange == "smooth" and settings.reverse_smooth_enable_pump:
                        continue
                    send_reverse_webhook(settings, log.symbol, curr_price, 'dump', logged_price, (threshold_price - logged_price) / logged_price * 100, exchange=log.exchange)
                elif log.type == 'dump' and curr_price >= threshold_price:
                    # Filter enable flags
                    if log.exchange == "rapid" and settings.reverse_rapid_enable_dump:
                        continue
                    if log.exchange == "smooth" and settings.reverse_smooth_enable_dump:
                        continue
                    send_reverse_webhook(settings, log.symbol, curr_price, 'pump', logged_price, (threshold_price - logged_price) / logged_price * 100, exchange=log.exchange)
        time.sleep(1)  # Частота проверки


def start_price_check_thread():
    check_thread = threading.Thread(target=check_prices)
    check_thread.start()


def update_price(settings: Settings, message: FuturesPrice, username: str | int):
    global price_history

    symbol = message.symbol
    if settings.use_only_usdt:
        if not symbol.endswith('USDT'):
            return
    if settings.coins_blacklist:
        if symbol in settings.coins_blacklist:
            return
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
                oi = sorted(get_oi_candles_minutes(symbol, max(2, SMOOTH_CHECK_MINUTES)), key=lambda x: x[0])
                oi_values = [float(x[1]) for x in oi]
                oi_change = (oi_values[-1] - oi_values[0]) / oi_values[0] * 100
                if abs(oi_change) > COI:
                    cvd_change = get_cvd_change(symbol, SMOOTH_CHECK_MINUTES+1)
                    if cvd_change > CCVD:
                        volumes_change = get_volumes_change(symbol, SMOOTH_CHECK_MINUTES+1)
                        if volumes_change > CVVC:
                            log_and_journal(symbol, change_amount_pump, "pump", "smooth", min_price, max_price, SMOOTH_CHECK_MINUTES, price_history[settings.user_id][symbol][-1][1])
            if change_amount_dump >= SMOOTH_PRICE_CHANGE and settings.smooth_enable_dump:
                oi = sorted(get_oi_candles_minutes(symbol, max(2, SMOOTH_CHECK_MINUTES)), key=lambda x: x[0])
                oi_values = [float(x[1]) for x in oi]
                oi_change = (oi_values[-1] - oi_values[0]) / oi_values[0] * 100
                if abs(oi_change) > COI:
                    cvd_change = get_cvd_change(symbol, SMOOTH_CHECK_MINUTES+1)
                    if -cvd_change > CCVD:
                        volumes_change = get_volumes_change(symbol, SMOOTH_CHECK_MINUTES+1)
                        if -volumes_change > CVVC:
                            log_and_journal(symbol, change_amount_dump, "dump", "smooth", min_price, max_price, SMOOTH_CHECK_MINUTES, price_history[settings.user_id][symbol][-1][1])
