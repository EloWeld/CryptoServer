from app.bacground_tasks.base import webhook_data
from app.models import ChangesLog, Settings, db
from app.utils import datetime, loguru, requests, send_tg_message, time


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
    subtype = data.get('subtype', 'default')
    data['usd_amount'] = settings.default_vol_usd if subtype == 'default' else settings.reverse_vol_usd
    if data['type'] != "error":
        send_webhook(settings, data['symbol'], data, now, user_id)

    if settings.tg_id and settings.tg_id > 1000:
        if data['type'] == "pump":
            send_tg_message(settings.tg_id, f"<b>🟢{'🔄' if subtype == 'reversal' else ''} Новый ПАМП {'от ревёрса!' if subtype == 'reversal' else '!'}</b>\n"
                            f"🪙 Монета: <code>{data['symbol']}</code> <a href='https://www.coinglass.com/tv/Binance_{data['symbol']}'>ССЫЛКА</a>\n"
                            f"🎯 Режим: <code>{data['exchange']}</code>\n"
                            f"📈 Изменение: <code>{data['change_amount']}</code> за <code>{data['interval']}</code> минут(-ы)\n"
                            f"🌐 Сайт: {settings.domain}\n"
                            f"📣 Сигналов за сутки: {len([x for x in change_log if x.created_at > datetime.datetime(nowd.year, nowd.month, nowd.day)])}")

        elif data['type'] == "dump":
            send_tg_message(settings.tg_id, f"<b>🔴{'🔄' if subtype == 'reversal' else ''} Новый ДАМП {'от ревёрса!' if subtype == 'reversal' else '!'}!</b>\n"
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
                              old_price=data.get('old_price', None),
                              curr_price=data.get('curr_price', None)))
    db.session.commit()


def send_webhook(settings: Settings, symbol, data, minute, user_id):
    if data['exchange'] == "rapid":
        url = settings.rapid_pump_webhook if data['type'] == 'pump' else settings.rapid_dump_webhook
        if 'subtype' in data and data['subtype'] == "reversal":
            data_template: str = settings.reverse_rapid_pump_data if data['type'] == 'pump' else settings.reverse_rapid_dump_data
        else:
            data_template: str = settings.rapid_pump_data if data['type'] == 'pump' else settings.rapid_dump_data
    elif data['exchange'] == "smooth":
        url = settings.smooth_pump_webhook if data['type'] == 'pump' else settings.smooth_dump_webhook
        if 'subtype' in data and data['subtype'] == "reversal":
            data_template: str = settings.reverse_smooth_pump_data if data['type'] == 'pump' else settings.reverse_smooth_dump_data
        else:
            data_template: str = settings.smooth_pump_data if data['type'] == 'pump' else settings.smooth_dump_data

    data = data_template.replace('{{ticker}}', symbol)
    if 'usd_amount' in data:
        data = data_template.replace('{{volume_usd}}', data['usd_amount'])

    # 6
    try:
        r = requests.post(url, headers={'Content-Type': "application/json"}, data=data)
        if r.status_code != 200:
            add_journal({"type": "error", "message": r.text,
                        "symbol": symbol, "created_at": datetime.datetime.now()}, settings, user_id)
    except Exception as e:
        add_journal({"type": "error", "message": str(
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
