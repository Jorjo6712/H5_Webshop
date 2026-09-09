from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session

from config import Config


class Base(DeclarativeBase):
    pass


engine = create_engine(Config.DATABASE_URL)


def get_session():
    return Session(engine)