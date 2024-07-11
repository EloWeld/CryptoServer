from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app.models import Settings, db

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/api/webhook/<webhook_id>', methods=['DELETE', 'GET'])
@login_required
def manage_webhook(webhook_id):
    user = current_user
    if request.method == 'DELETE':
        settings: Settings = Settings.query.filter_by(user_id=user.id).first()
        if not settings:
            return jsonify({"result": "settings not found"}), 404

        try:
            updated_webhooks = settings.webhooks.copy()
            updated_webhooks = [x for x in updated_webhooks if x.get('webhook', None) != webhook_id]
            settings.webhooks = updated_webhooks

            db.session.commit()
            return jsonify({"result": "ok", "settings": settings}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"result": "error", "message": str(e)}), 500

    return jsonify({"result": "not_allowed"}), 405


@settings_bp.route('/api/webhook', methods=['POST', 'GET'])
@login_required
def manage_webhooks():
    user = current_user
    if request.method == 'POST':
        data = request.json
        if not data:
            return jsonify({"result": "invalid_data"}), 400

        settings: Settings = Settings.query.filter_by(user_id=user.id).first()
        if not settings:
            settings = Settings(user_id=user.id)
            db.session.add(settings)

        try:
            data['delay'] = int(data['delay'])
            data['calls_amount'] = int(data['calls_amount'])
            updated_webhooks = settings.webhooks.copy()
            updated_webhooks.append(data)
            settings.webhooks = updated_webhooks

            db.session.commit()
            return jsonify({"result": "ok"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"result": "error", "message": str(e)}), 500

    return jsonify({"result": "not_allowed"}), 405


@settings_bp.route('/api/settings', methods=['GET', 'POST'])
@login_required
def manage_settings():
    user = current_user
    if request.method == 'POST':
        data = request.json
        settings = Settings.query.filter_by(user_id=user.id).first()
        if not settings:
            settings = Settings(user_id=user.id)
        settings.webhooks = data.get('webhooks', [])
        settings.received_hooks = data.get('received_hooks', [])
        settings.blocked_hooks = data.get('blocked_hooks', 0)
        settings.domain = data.get('domain', "https://www.davinchi-crypto.ru/api")

        settings.rapid_pump_webhook = data.get('rapid_pump_webhook', "https://hook.finandy.com/?")
        settings.rapid_dump_webhook = data.get('rapid_dump_webhook', "https://hook.finandy.com/?")
        settings.rapid_pump_data = data.get('rapid_pump_data', "{}")
        settings.rapid_dump_data = data.get('rapid_dump_data', "{}")
        settings.rapid_enable_pump = data.get('rapid_enable_pump', True)
        settings.rapid_enable_dump = data.get('rapid_enable_dump', True)

        settings.smooth_pump_webhook = data.get('smooth_pump_webhook', "https://hook.finandy.com/?")
        settings.smooth_dump_webhook = data.get('smooth_dump_webhook', "https://hook.finandy.com/?")
        settings.smooth_pump_data = data.get('smooth_pump_data', "{}")
        settings.smooth_dump_data = data.get('smooth_dump_data', "{}")
        settings.smooth_enable_pump = data.get('smooth_enable_pump', True)
        settings.smooth_enable_dump = data.get('smooth_enable_dump', True)

        settings.reverse_rapid_pump_webhook = data.get('reverse_rapid_pump_webhook', "https://hook.finandy.com/?")
        settings.reverse_rapid_dump_webhook = data.get('reverse_rapid_dump_webhook', "https://hook.finandy.com/?")
        settings.reverse_rapid_pump_data = data.get('reverse_rapid_pump_data', settings.reverse_rapid_pump_data)
        settings.reverse_rapid_dump_data = data.get('reverse_rapid_dump_data', settings.reverse_rapid_dump_data)
        settings.reverse_rapid_enable_pump = data.get('reverse_rapid_enable_pump', settings.reverse_rapid_enable_pump)
        settings.reverse_rapid_enable_dump = data.get('reverse_rapid_enable_dump', settings.reverse_rapid_enable_dump)
        settings.reverse_smooth_pump_webhook = data.get('reverse_smooth_pump_webhook', "https://hook.finandy.com/?")
        settings.reverse_smooth_dump_webhook = data.get('reverse_smooth_dump_webhook', "https://hook.finandy.com/?")
        settings.reverse_smooth_pump_data = data.get('reverse_smooth_pump_data', settings.reverse_smooth_pump_data)
        settings.reverse_smooth_dump_data = data.get('reverse_smooth_dump_data', settings.reverse_smooth_dump_data)
        settings.reverse_smooth_enable_pump = data.get('reverse_smooth_enable_pump', settings.reverse_smooth_enable_pump)
        settings.reverse_smooth_enable_dump = data.get('reverse_smooth_enable_dump', settings.reverse_smooth_enable_dump)

        settings.default_vol_usd = data.get('default_vol_usd', settings.default_vol_usd)
        settings.reverse_vol_usd = data.get('reverse_vol_usd', settings.reverse_vol_usd)
        settings.reverse_last_order_dist = data.get('reverse_last_order_dist', settings.reverse_last_order_dist)
        settings.reverse_full_orders_count = data.get('reverse_full_orders_count', settings.reverse_full_orders_count)
        settings.reverse_orders_count = data.get('reverse_orders_count', settings.reverse_orders_count)
        settings.reverse_multiplier = data.get('reverse_multiplier', settings.reverse_multiplier)
        settings.reverse_density = data.get('reverse_density', settings.reverse_density)

        settings.check_per_minutes_rapid = int(data.get('check_per_minutes_rapid', 1))
        settings.check_per_minutes_smooth = int(data.get('check_per_minutes_smooth', 3))
        settings.rapid_delay = data.get('rapid_delay', 3)
        settings.smooth_delay = data.get('smooth_delay', 3)

        settings.max_save_minutes = data.get('max_save_minutes', 15)
        settings.price_change_percent = data.get('price_change_percent', 2.0)
        settings.price_change_trigger_percent = data.get('price_change_trigger_percent', 4.0)
        settings.oi_change_percent = data.get('oi_change_percent', 4.0)
        settings.cvd_change_percent = data.get('cvd_change_percent', 4.0)
        settings.v_volumes_change_percent = data.get('v_volumes_change_percent', 4.0)
        settings.tg_id = data.get('tg_id', -1)

        settings.use_spot = data.get('use_spot', False)
        settings.use_wicks = data.get('use_wicks', False)
        settings.use_only_usdt = data.get('use_only_usdt', False)
        settings.coins_blacklist = data.get('coins_blacklist', [])

        db.session.add(settings)
        db.session.commit()
        return jsonify({"message": "Settings updated"}), 200

    settings: Settings = Settings.query.filter_by(user_id=user.id).first()
    if settings:
        return jsonify(settings), 200
    else:
        # Создание настроек с стандартными значениями
        default_settings = Settings(
            user_id=user.id,

            check_per_minutes_rapid=1,
            check_per_minutes_smooth=3,

            price_change_percent=2.0,
            price_change_trigger_percent=4.0,

            max_save_minutes=15,
            oi_change_percent=4.0,
            cvd_change_percent=4.0,
            v_volumes_change_percent=4.0,
        )
        db.session.add(default_settings)
        db.session.commit()
        return jsonify(default_settings), 200
