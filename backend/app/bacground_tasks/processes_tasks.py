from copy import deepcopy
import datetime
import threading
from flask import Flask, current_app
from app import socketio
from app.bacground_tasks.base import lock, process_running, process_threads
from app.bacground_tasks.check_prices import update_price
from app.models import FuturesPrice, ParsingProcess, Settings, SpotPrice, User, db
from app.utils import get_futures_prices, get_spot_prices, loguru, time


import loguru
from sqlalchemy.orm import scoped_session, sessionmaker


import time
import traceback

global_f_prices = []
global_s_prices = []


def save_prices_to_db(app):
    global global_f_prices
    global global_s_prices
    with app.app_context():
        engine = db.get_engine()
        Session = scoped_session(sessionmaker(bind=engine))
        session = Session()
        while True:
            try:
                spot_prices = get_spot_prices()
                futures_prices = get_futures_prices()
                # for x in futures_prices:
                #     ts = x['time'] / 1000 // 60
                #     ns = datetime.datetime.now().timestamp() // 60
                #     if ts != ns:
                #         print(x['symbol'], ts, ns)
                global_f_prices = [FuturesPrice(symbol=price['symbol'], price=price['price']) for price in futures_prices]
                global_s_prices = [SpotPrice(symbol=price['symbol'], price=price['price']) for price in spot_prices]

                session.query(SpotPrice).delete(synchronize_session='evaluate')
                session.query(FuturesPrice).delete(synchronize_session='evaluate')
                for price in spot_prices:
                    session.add(SpotPrice(symbol=price['symbol'], price=price['price']))
                for price in futures_prices:
                    session.add(FuturesPrice(symbol=price['symbol'], price=price['price']))

                with lock:
                    session.commit()
            except Exception as e:
                loguru.logger.error(f"Error fetching prices from binance: {e} {traceback.format_exc()}")
            time.sleep(2)


def start_price_saving_thread():
    app = current_app._get_current_object()
    price_thread = threading.Thread(target=save_prices_to_db, args=(app,))
    price_thread.start()


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
                with lock:
                    process = session.query(ParsingProcess).filter(ParsingProcess.user_id == user.id, ParsingProcess.status == "active").first()
                    us: Settings = session.query(Settings).filter(Settings.user_id == user.id).first()
                if us.use_spot:
                    prices = global_s_prices
                else:
                    prices = global_f_prices
                for price in prices:
                    try:
                        update_price(us, price, user_id)
                    except Exception as e:
                        err_msg = f"Error in cycle update price: {e} {traceback.format_exc()}"
                        loguru.logger.error(err_msg)
                        socketio.emit('log', {'data': err_msg}, room=user_id)

                time.sleep(0.5)
            loguru.logger.info(f"Process has stopped for user {user_id} {user.username}")
            socketio.emit('log', {'data': f'Process has stopped for user {user_id} {user.username}.'}, room=user_id)
            process_running[user_id] = False
            if user_id in process_threads:
                del process_threads[user_id]
        except Exception as err:
            loguru.logger.error(f"Error on check prices {err} {traceback.format_exc()}")
        finally:
            session.close()


def start_user_processes():
    app = current_app._get_current_object()
    running_processes = db.session.query(ParsingProcess).filter(ParsingProcess.status == "active")
    for running_process in running_processes:
        price_thread = threading.Thread(target=process_function, args=(app, running_process.user_id))
        price_thread.start()
