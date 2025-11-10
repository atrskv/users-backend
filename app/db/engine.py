import logging
import os

from sqlalchemy.orm import Session
from sqlmodel import SQLModel, create_engine, text

from app.models.user import User

engine = create_engine(
    os.getenv("DATABASE_ENGINE", ""),
    pool_size=int(os.getenv("DATABASE_POOL_SIZE", 10)),
)


def init_db():
    SQLModel.metadata.create_all(engine)


def check_availability():
    try:
        with Session(engine) as s:
            s.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logging.error(e)
        return False


users_list: list[User] = []
