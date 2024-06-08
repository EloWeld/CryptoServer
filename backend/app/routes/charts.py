import time
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from dataclasses import asdict
from app.routes.processes import process_running, price_history
from app.models import ChangesLog, ParsingProcess, Settings, db
from app.utils import get_cvd, get_cvd_change, get_oi_candles, get_oi_candles_minutes, get_volumes, get_volumes_change

charts_bp = Blueprint('charts', __name__)

last_hook_time = {}


@charts_bp.route('/api/coins', methods=['GET'])
def coins():
    running_process = db.session.query(ParsingProcess).filter(ParsingProcess.user_id == current_user.id, ParsingProcess.status == "active").first()
    if running_process is None:
        return jsonify({"message": "NO_PROCESS"}), 404
    user_price_history: dict = price_history.get(current_user.id, None)
    if user_price_history is None:
        return jsonify({"message": "NO_PRICE_HISTORY"}), 200

    coins = sorted(list(user_price_history.keys()))

    return jsonify([{"id": x, "name": x} for x in coins]), 200


@charts_bp.route('/api/coins/<coin>/chart', methods=['GET'])
def coin_chart(coin: str):
    running_process = db.session.query(ParsingProcess).filter(ParsingProcess.user_id == current_user.id, ParsingProcess.status == "active").first()
    if running_process is None:
        return jsonify({"message": "NO_PROCESS"}), 200

    user_price_history = price_history.get(current_user.id, None)
    if user_price_history is None:
        return jsonify({"message": "NO_PRICE_HISTORY"}), 200
    symbol_history = user_price_history[coin]
    if symbol_history is None:
        return jsonify({"message": "NO_COIN_PRICE_HISTORY"}), 200

    period = len(symbol_history)
    oi_data = get_oi_candles_minutes(coin, period)
    cvd = get_cvd(coin, period)
    volumes = get_volumes(coin, limit=period)

    enriched_data = {
        "oi": oi_data,
        "cvd": cvd,
        "volumes": volumes,
        "price": symbol_history
    }

    return jsonify(enriched_data), 200
