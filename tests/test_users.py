from http import HTTPStatus

import pytest
import requests

from users_backend.models.user import User


@pytest.fixture(autouse=False)
def users_items(app_url: str):
    response = requests.get(f"{app_url}/api/users")
    assert response.status_code == HTTPStatus.OK
    return response.json()["items"]


@pytest.mark.usefixtures("prepare_users_data")
class TestShowUsers:
    @pytest.mark.parametrize("user_id", [1, 6, 12])
    def test_show_user(self, app_url: str, user_id: int):
        response = requests.get(f"{app_url}/api/users/{user_id}")

        user = response.json()

        assert response.status_code == HTTPStatus.OK
        _ = User.model_validate(user)

    def test_show_users(self, app_url: str):
        response = requests.get(f"{app_url}/api/users/")

        users_page = response.json()
        users_items = users_page["items"]

        assert response.status_code == HTTPStatus.OK
        for user in users_items:
            _ = User.model_validate(user)

    def test_show_no_duplicates_users(
        self, users_items: list[dict[str, str | int]]
    ):
        users_ids: list[str | int] = [user["id"] for user in users_items]

        assert len(users_ids) == len(set(users_ids))


@pytest.mark.usefixtures("clear_users_data")
class TestShowNonExistentUsers:
    @pytest.mark.parametrize("user_id", [13])
    def test_show_nonexistent_user(self, app_url: str, user_id: int):
        response = requests.get(f"{app_url}/api/users/{user_id}")

        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
    def test_show_user_with_invalid_id(self, app_url: str, user_id: int):
        response = requests.get(f"{app_url}/api/users/{user_id}")

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
