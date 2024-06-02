import datetime
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user
import jwt
from app.models import User
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        login_user(user)
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.datetime.now() + datetime.timedelta(days=300) 
        }, Config.SECRET_KEY, algorithm='HS256')
        return jsonify({"message": "Login successful", "token": token}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"}), 200


