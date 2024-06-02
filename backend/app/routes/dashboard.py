from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from dataclasses import asdict

from app.models import ChangesLog

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api/dashboard', methods=['GET'])
@login_required
def dashboard():
    return jsonify({"message": f"Welcome, {current_user.username}!"})

@dashboard_bp.route('/api/changes_log', methods=['GET'])
@login_required
def get_changes_log():
    current_user.id
    logs = ChangesLog.query.order_by(ChangesLog.created_at.desc()).limit(2000)
    return jsonify([asdict(log) for log in logs])