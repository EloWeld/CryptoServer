from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models import User, db

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/user', methods=['GET'])
@login_required
def get_user():
    user = current_user
    user_data = {
        "id": user.id,
        "username": user.username,
        "timezone_offset": user.timezone_offset
    }
    return jsonify(user_data), 200

@user_bp.route('/api/user/timezone', methods=['POST'])
@login_required
def update_timezone():
    data = request.json
    timezone_offset = data.get('timezone_offset')

    if timezone_offset is not None:
        current_user.timezone_offset = timezone_offset
        db.session.commit()
        return jsonify({"message": "Timezone updated successfully"}), 200
    else:
        return jsonify({"error": "Invalid timezone offset"}), 400
