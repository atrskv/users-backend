import json
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, Params, paginate

from app.db import users
from app.models.user import User, UserCreate, UserUpdate
from app.utils import get_pagination_params

router = APIRouter(prefix="/api/users")


@router.post("/", status_code=HTTPStatus.CREATED)
def add_users():
    global users_list

    users_list.clear()

    with open("app/users.json") as f:
        users_data = json.load(f)

    for user_dict in users_data:
        users_list.append(User.model_validate(user_dict))


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


@router.delete("/", status_code=HTTPStatus.OK)
def clear_users():
    global users_list

    users_list.clear()

    return users_list


@router.post("/", status_code=HTTPStatus.CREATED)
def create_user(user: User) -> User:
    UserCreate.model_validate(user.model_dump())
    return users.create_user(user)


@router.patch("/{user_id}", status_code=HTTPStatus.OK)
def update_user(user_id: int, user: User) -> User:
    if user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Invalid user id",
        )
    UserUpdate.model_validate(user.model_dump())
    return users.update_user(user_id, user)


@router.delete("/{user_id}", status_code=HTTPStatus.OK)
def delete_user(user_id: int):
    if user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Invalid user id",
        )
    users.delete_user(user_id)
    return {"message": "User deleted"}
