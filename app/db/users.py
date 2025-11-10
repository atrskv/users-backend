from collections.abc import Iterable

from fastapi import HTTPException
from sqlmodel import Session, delete, select

from app.db.engine import engine
from app.models.user import User


def create_user(user: User) -> User:
    with Session(engine) as s:
        s.add(user)
        s.commit()
        s.refresh(user)

        return user


def get_user(user_id: int) -> User | None:
    with Session(engine) as s:
        return s.get(User, user_id)


def get_users() -> Iterable[User] | None:
    with Session(engine) as s:
        statement = select(User)

        return s.exec(statement).all()


def update_user(user_id: int, user: User) -> User | None:
    with Session(engine) as session:
        db_user = session.get(User, user_id)

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        user_data = user.model_dump(exclude_unset=True)
        _ = db_user.sqlmodel_update(user_data)

        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return db_user


def delete_user(user_id: int):
    with Session(engine) as s:
        user = s.get(User, user_id)
        s.delete(user)
        s.commit()


def clear_users():
    with Session(engine) as session:
        statement = delete(User)
        session.exec(statement)
        session.commit()
