from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from dataclasses import asdict
from sqlalchemy import desc

from app.models import ChangesLog

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/api/dashboard', methods=['GET'])
@login_required
def dashboard():
    return jsonify({"message": f"Welcome, {current_user.username}!"})


@dashboard_bp.route('/api/changes_log', methods=['GET'])
@login_required
def get_changes_log():
    logs = ChangesLog.query.filter(ChangesLog.user_id == current_user.id).order_by(ChangesLog.created_at.desc()).limit(1000)
    return jsonify([asdict(log) for log in logs])
