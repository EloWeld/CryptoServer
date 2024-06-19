import threading

from app.utils import Config

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


webhook_data = {}
price_history = {}
process_threads = {}
process_running = {}
lock = threading.Lock()


def connect_to_db():
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session
