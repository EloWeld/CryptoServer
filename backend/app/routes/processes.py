# app/routes/dashboard.py
import cmath
import math
from flask import Blueprint, current_app, jsonify, request
from flask_login import login_required, current_user
from flask_socketio import emit, join_room, leave_room
import jwt
from app import socketio
import threading
import loguru

from app.bacground_tasks.processes_tasks import process_function
from app.bacground_tasks.base import process_threads
from app.models import ParsingProcess, User, db
from app.utils import *

processes_bp = Blueprint('processes', __name__)


@processes_bp.route('/api/start_process', methods=['POST'])
@login_required
def start_process():
    user_id = current_user.id
    running_process = db.session.query(ParsingProcess).filter(ParsingProcess.user_id == user_id).first()
    if running_process is None:
        db.session.add(ParsingProcess(user_id=user_id, status="active"))
        db.session.commit()
        running_process = db.session.query(ParsingProcess).filter(ParsingProcess.user_id == user_id).first()
    
    # Остановим процесс если есть
    if user_id in process_threads:
        process_threads[user_id].join()
        try:
            del process_threads[user_id]
        except Exception as e:
            loguru.logger.error(str(e))
    
    running_process.status = "running"
    db.session.commit()
    
    # И сделаем новый
    app = current_app._get_current_object()  # Wattafock? Works! Magick!
    process_thread = threading.Thread(target=process_function, args=(app, user_id,))
    process_threads[user_id] = process_thread
    process_thread.start()
    
    return jsonify({'status': 'Process started'})


@processes_bp.route('/api/get_process_status', methods=['GET'])
@login_required
def get_process_status():
    user_id = current_user.id
    running_process = db.session.query(ParsingProcess).filter(ParsingProcess.user_id == user_id).first()
    return jsonify({"is_running": running_process is not None and running_process.status == "active"}), 200


@processes_bp.route('/api/stop_process', methods=['POST'])
@login_required
def stop_process():
    user_id = current_user.id
    running_process = db.session.query(ParsingProcess).filter(ParsingProcess.user_id == user_id).first()
    if running_process is None:
        return jsonify({"status": "Process is not running now"})

    running_process.status = "finished"
    running_process.ended_at = datetime.datetime.now()

    db.session.commit()

    if user_id in process_threads:
        process_threads[user_id].join()
        try:
            del process_threads[user_id]
        except Exception as e:
            loguru.logger.error(str(e))
    return jsonify({'status': 'Process stopped'})


@socketio.on('connect')
def connect(auth: dict):
    token = auth.get('token', None) if auth else None
    if not token:
        loguru.logger.error(f"Disconnect, no token {auth}")

        disconnect()
        return False
    try:
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        user = User.query.get(data['user_id'])
        if user:
            loguru.logger.info(f"Connect to server!")
            # Присоединение пользователя к комнате
            join_room(user.id)
            emit('log', {'data': f'Connected to server as {user.username}'}, room=user.id)
        else:
            disconnect()
            return False
    except Exception as e:
        loguru.logger.error(f"Connection rejected: {e}")
        disconnect()
        return False


@socketio.on('disconnect')
def disconnect():
    if current_user.is_authenticated:
        leave_room(current_user.id)
