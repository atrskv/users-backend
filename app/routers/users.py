from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params, paginate

from app.db import users
from app.models.user import User, UserCreate, UserUpdate
from app.utils import get_pagination_params

router = APIRouter(prefix="/api/users")


@router.delete("/clear", status_code=HTTPStatus.OK)
def clear_users():
    return users.clear_users()


@router.post("/", status_code=HTTPStatus.CREATED)
def create_user(user: UserCreate) -> User:
    db_user = User(**user.model_dump())
    return users.create_user(db_user)


@router.get("/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int) -> User:
    if user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Invalid user id",
        )

    user = users.get_user(user_id)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )

    return user


@router.get("/", status_code=HTTPStatus.OK)
def get_users(params: Params = Depends(get_pagination_params)) -> Page[User]:
    return paginate(users.get_users(), params)


@router.patch("/{user_id}", status_code=HTTPStatus.OK)
def update_user(user_id: int, user: UserUpdate) -> User:
    if user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Invalid user id",
        )
    db_user = User(**user.model_dump(exclude_unset=True))

    return users.update_user(user_id, db_user)


@router.delete("/{user_id}", status_code=HTTPStatus.OK)
def delete_user(user_id: int):
    if user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Invalid user id",
        )
    users.delete_user(user_id)

    return {"message": "User deleted"}
