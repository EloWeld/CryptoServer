import time
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from dataclasses import asdict

from app.models import ChangesLog, Settings, db

hooks_bp = Blueprint('hooks', __name__)

last_hook_time = {}


@hooks_bp.route('/api/webhook/<hook_id>', methods=['POST', 'GET'])
def webhook(hook_id: str):
    if request.method == "GET":
        return jsonify({"message": "Na-ah! Only POST"}), 400
    if request.content_type != "application/json":
        return jsonify({"message": "Na-ah! Need body, application/json"}), 400

    data = request.json
    current_time = time.time()

    hook = None

    settings_all: list[Settings] = Settings.query.all()
    settings = None
    for setting in settings_all:
        for hook in setting.webhooks:
            if hook['webhook'] == hook_id:
                hook = hook
                settings = setting
    if hook is None:
        return jsonify({"message": "Hook not found"}), 400
    delay = hook['delay']
    strategy = hook['strategy']
    calls_amount = hook['calls_amount']
    hook_calls: list[float] = hook.get('hook_calls', [])

    if strategy == 'single':
        if hook_id in last_hook_time:
            time_since_last_hook = current_time - last_hook_time[hook_id]
            if time_since_last_hook < delay:
                settings.blocked_hooks = settings.blocked_hooks + 1
                db.session.commit()
                return jsonify({"status": "ignored", "reason": f"Less than {delay} seconds since last hook"}), 200

    elif strategy == 'mult':
        hook_calls.append(current_time)

        # Remove old calls outside of the delay window
        hook_calls = [t for t in hook_calls if current_time - t <= delay]
        hook['hook_calls'] = hook_calls
        settings.webhooks = [x for x in settings.webhooks if x['webhook'] != hook_id] + [hook]
        db.session.commit()

        if len(hook_calls) < int(calls_amount):
            return jsonify({"status": "waiting", "reason": f"Received {len(hook_calls)}/{calls_amount} calls"}), 200

        # Reset count after threshold is reached
        hook_calls = []

        hook['hook_calls'] = hook_calls
        settings.webhooks = [x for x in settings.webhooks if x['webhook'] != hook_id] + [hook]
        db.session.commit()

    last_hook_time[hook_id] = current_time
    settings.received_hooks = settings.received_hooks + [{"hook_id": hook_id, "time": current_time}]
    db.session.commit()
    forward_hook(data, hook['redirect_to_url'])

    return jsonify({"status": "forwarded"}), 200


def forward_hook(data, redirect_to):
    import requests
    headers = {'Content-Type': 'application/json'}
    response = requests.post(redirect_to, json=data, headers=headers)
    return response
