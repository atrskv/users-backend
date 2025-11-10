from collections.abc import Iterable

from sqlmodel import Session, select

from app.db.engine import engine
from app.models.user import User


def get_user(user_id: int) -> User | None:
    with Session(engine) as s:
        return s.get(User, user_id)


def get_users() -> Iterable[User] | None:
    with Session(engine) as s:
        statement = select(User)
        return s.exec(statement).all()
