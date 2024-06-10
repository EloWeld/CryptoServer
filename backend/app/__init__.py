import sys
from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
import jwt
import loguru
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
socketio = SocketIO()


@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*", manage_session=True, path='/api/socket.io')

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.settings import settings_bp
    from app.routes.user import user_bp
    from app.routes.processes import processes_bp
    from app.routes.hooks import hooks_bp
    from app.routes.charts import charts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(processes_bp)
    app.register_blueprint(hooks_bp)
    app.register_blueprint(charts_bp)

    if len(sys.argv) > 1 and sys.argv[1] not in ['db', 'migrate', 'upgrade', 'downgrade']:
        with app.app_context():
            from app.routes.processes import start_price_saving_thread, start_user_processes
            start_price_saving_thread()
            start_user_processes()

    return app
