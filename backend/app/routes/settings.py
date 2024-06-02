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
        settings.domain = data.get('domain', "https://www.davinchi-crypto.ru")
        settings.pump_webhook = data.get('pump_webhook', "https://hook.finandy.com/?")
        settings.dump_webhook = data.get('dump_webhook', "https://hook.finandy.com/?")
        settings.pump_data = data.get('pump_data', "{}")
        settings.dump_data = data.get('dump_data', "{}")
        settings.enable_pump = data.get('enable_pump', True)
        settings.enable_dump = data.get('enable_dump', True)
        settings.check_per_minutes = data.get('check_per_minutes', 1)
        settings.check_per_minutes_mode_2 = data.get('check_per_minutes_mode_2', 3)
        settings.max_save_minutes = data.get('max_save_minutes', 15)
        settings.price_change_percent = data.get('price_change_percent', 2.0)
        settings.price_change_trigger_percent = data.get('price_change_trigger_percent', 4.0)
        settings.oi_change_percent = data.get('oi_change_percent', 4.0)
        settings.cvd_change_percent = data.get('cvd_change_percent', 4.0)
        settings.v_volumes_change_percent = data.get('v_volumes_change_percent', 4.0)
        settings.use_spot = data.get('use_spot', False)
        settings.use_wicks = data.get('use_wicks', False)
        settings.tg_id = data.get('tg_id', -1)
        
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
            webhooks=[],
            received_hooks=[],
            blocked_hooks=0,
            domain="https://www.davinchi-crypto.ru",
            pump_webhook="https://hook.finandy.com/?",
            dump_webhook="https://hook.finandy.com/?",
            pump_data="{}",
            dump_data="{}",
            enable_pump=True,
            enable_dump=True,
            check_per_minutes=1,
            check_per_minutes_mode_2=3,
            max_save_minutes=15,
            price_change_percent=2.0,
            price_change_trigger_percent=4.0,
            oi_change_percent=4.0,
            cvd_change_percent=4.0,
            v_volumes_change_percent=4.0,
            use_spot=False,
            use_wicks=False,
            tg_id=-1
        )
        db.session.add(default_settings)
        db.session.commit()
        return jsonify(default_settings), 200