import json
from http import HTTPStatus

import uvicorn
from fastapi import FastAPI, HTTPException

from users_backend.models.status import AppStatus
from users_backend.models.user import User

app: FastAPI = FastAPI()

users_list: list[User] = []


@app.get("/api/status", status_code=HTTPStatus.OK)
def get_status() -> AppStatus:
    return AppStatus(users=bool(users_list))


@app.get("/api/users/{user_id}", status_code=HTTPStatus.OK)
def get_user(user_id: int) -> User:
    if user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Invalid user id",
        )
    if user_id > len(users_list):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )
    return users_list[user_id - 1]


@app.get("/api/users/", status_code=HTTPStatus.OK)
def get_users() -> list[User]:
    return users_list


if __name__ == "__main__":
    with open("users_backend/users.json") as f:
        users_list: list[dict[str, object]] = json.load(f)

    for user in users_list:
        _ = User.model_validate(user)

    uvicorn.run(app, host="localhost", port=8002)
