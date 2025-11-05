from http import HTTPStatus

import pytest
import requests

from users_backend.models.user import User


@pytest.fixture
def users(app_url: str):
    response = requests.get(f"{app_url}/api/users/")
    assert response.status_code == HTTPStatus.OK
    return response.json()


@pytest.mark.parametrize("user_id", [1, 6, 12])
def test_show_user(app_url: str, user_id: int):
    response = requests.get(f"{app_url}/api/users/{user_id}")

    user = response.json()

    assert response.status_code == HTTPStatus.OK
    _ = User.model_validate(user)


def test_show_users(app_url: str):
    response = requests.get(f"{app_url}/api/users/")

    users = response.json()

    assert response.status_code == HTTPStatus.OK
    for user in users:
        _ = User.model_validate(user)


def test_show_no_duplicates_users(users: list[dict[str, str | int]]):
    users_ids: list[str | int] = [user["id"] for user in users]

    assert len(users_ids) == len(set(users_ids))


@pytest.mark.parametrize("user_id", [13])
def test_show_nonexistent_user(app_url: str, user_id: int):
    response = requests.get(f"{app_url}/api/users/{user_id}")

    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
def test_user_invalid_values(app_url: str, user_id: int):
    response = requests.get(f"{app_url}/api/users/{user_id}")

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
