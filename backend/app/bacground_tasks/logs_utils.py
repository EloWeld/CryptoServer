from app.bacground_tasks.base import webhook_data
from app.models import ChangesLog, Settings, db
from app.utils import datetime, loguru, requests, send_tg_message, time
from sqlalchemy.exc import SQLAlchemyError


def add_journal(data: dict, settings: Settings, user_id: str | int):
    # Чтение существующего журнала, последние 10 элементов для юзера
    last_logs: list[ChangesLog] = ChangesLog.query.filter(ChangesLog.user_id == user_id).order_by(ChangesLog.created_at.desc()).limit(300)

    # Проверка на дублирование
    nowd = datetime.datetime.now()
    now = (int(nowd.timestamp()) // 60) * 60
    delay = 1
    for log_entry in last_logs[:10]:
        delay = 1
        if 'exchange' in data:
            if "rapid" == data['exchange']:
                delay = settings.rapid_delay
            elif "smooth" == data['exchange']:
                delay = settings.smooth_delay

        if log_entry.symbol == data["symbol"] and datetime.datetime.now() - log_entry.created_at < datetime.timedelta(minutes=delay):
            return  # Запись уже существует, не добавляем дубликат
    subtype = data.get('subtype', 'default')

    data['usd_amount'] = settings.default_vol_usd if subtype == 'default' else settings.reverse_vol_usd
    if data['type'] != "error":
        send_webhook(settings, data['symbol'], data, now, user_id)
    if subtype == "reversal":
        data['exchange'] += "_reversal"
    if settings.tg_id and settings.tg_id > 1000:
        ca = str(data['change_amount'])[:5] if 'change_amount' in data else 'unknown'
        if data['type'] == "pump":
            send_tg_message(settings.tg_id, f"<b>🟢{'🔄' if subtype == 'reversal' else ''} Новый ПАМП {'от ревёрса!' if subtype == 'reversal' else '!'}</b>\n"
                            f"🪙 Монета: <code>{data['symbol']}</code> <a href='https://www.coinglass.com/tv/Binance_{data['symbol']}'>ССЫЛКА</a>\n"
                            f"🎯 Режим: <code>{data['exchange']}</code>\n"
                            f"📈 Изменение: <code>{ca}</code> за <code>{data['interval']}</code> минут(-ы)\n"
                            f"🌐 Сайт: {settings.domain}\n"
                            f"📣 Сигналов за сутки: {len([x for x in last_logs if x.created_at > datetime.datetime(nowd.year, nowd.month, nowd.day)])}")

        elif data['type'] == "dump":
            send_tg_message(settings.tg_id, f"<b>🔴{'🔄' if subtype == 'reversal' else ''} Новый ДАМП {'от ревёрса!' if subtype == 'reversal' else '!'}!</b>\n"
                            f"🪙 Монета: <code>{data['symbol']}</code> <a href='https://www.coinglass.com/tv/Binance_{data['symbol']}'>ССЫЛКА</a>\n"
                            f"🎯 Режим: <code>{data['exchange']}</code>\n"
                            f"📉 Изменение: <code>-{ca}</code> за <code>{data['interval']}</code> минут(-ы)\n"
                            f"🌐 Сайт: {settings.domain}\n"
                            f"📣 Сигналов за сутки: {len([x for x in last_logs if x.created_at > datetime.datetime(nowd.year, nowd.month, nowd.day)])}")
        else:
            send_tg_message(settings.tg_id, f"<b>⚠️ Странное поведение!</b>\n"
                            f"Данные: <code>{data}</code>")

    def ensure_limit_changes_log(limit=10000):
        count = ChangesLog.query.count()
        if count > limit:
            oldest_entries = ChangesLog.query.order_by(ChangesLog.created_at).limit(count - limit).all()
            for entry in oldest_entries:
                db.session.delete(entry)
            db.session.commit()
    ensure_limit_changes_log()
    loguru.logger.info(str(data) + f" {user_id}")

    db.session.add(ChangesLog(user_id=user_id,
                              exchange=data.get('exchange', None),
                              symbol=data.get('symbol', None),
                              type=data.get('type', None),
                              mode=data.get('mode', None),
                              change_amount=str(data.get('change_amount', None))[:4],
                              interval=data.get('interval', None),
                              created_at=datetime.datetime.now(),
                              old_price=data.get('old_price', None),
                              curr_price=data.get('curr_price', None)))
    db.session.commit()


def send_webhook(settings: Settings, symbol, data, minute, user_id):
    data_template = None
    pref = ""
    if 'subtype' in data and data['subtype'] == "reversal":
        pref += "reverse_"
    if "rapid" in data['exchange']:
        pref += "rapid_"
    elif "smooth" in data['exchange']:
        pref += "smooth_"
    if data['type'] == 'pump':
        pref += "pump_"
    elif data['type'] == 'dump':
        pref += "dump_"
    
    url = getattr(settings, f"{pref}webhook")
    data_template = getattr(settings, f"{pref}data")
            
    if data_template:
        data_for_send = data_template.replace('{{ticker}}', symbol)
        if 'usd_amount' in data:
            data_for_send = data_for_send.replace('{{volume_usd}}', str(data['usd_amount']))
    else:
        loguru.logger.error(f"Not data template! {data_template}")
    # 6
    try:
        r = requests.post(url, headers={'Content-Type': "application/json"}, data=data_for_send)
        if r.status_code != 200:
            add_journal({"type": "error", "message": "Не смог отправить вебхук", "data_to_send":data_for_send, "used_url": url, "used_pathes": pref, "detailed": r.text,
                        "symbol": symbol, "created_at": datetime.datetime.now()}, settings, user_id)
    except Exception as e:
        add_journal({"type": "error", "message": "Ошибка при отправке вебхука", "data_to_send":data_for_send, "used_url": url, "used_pathes": pref, "detailed": str(
            e), "symbol": symbol, "created_at": datetime.datetime.now()}, settings, user_id)


def send_reverse_webhook(settings: Settings, symbol, current_price, direction, old_price, change_amount, exchange='rapid'):
    data = {
        'symbol': symbol,
        'price': current_price,
        'type': direction,
        'exchange': exchange,
        'change_amount': change_amount,
        'subtype': 'reversal',
        'interval': 0,
        'old_price': old_price,
        'curr_price': current_price
    }
    add_journal(data, settings, settings.user_id)
    # send_webhook(settings, symbol, data, int(time.time()), user_id)
