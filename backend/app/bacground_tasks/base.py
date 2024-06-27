from functools import lru_cache
import threading

from app.utils import Config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


webhook_data = {}
price_history = {}
last_positions_story = {}
process_threads = {}
process_running = {}
lock = threading.Lock()


def connect_to_db():
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


@lru_cache(maxsize=128)
def get_settings(user_id):
    from app.models import Settings
    session = connect_to_db()
    with session:
        return session.query(Settings).filter(Settings.user_id == user_id).first()
