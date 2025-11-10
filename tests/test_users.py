from http import HTTPStatus

import pytest
import requests

from app.models.user import User


@pytest.fixture(autouse=False)
def users_items(app_url: str):
    response = requests.get(f"{app_url}/api/users")
    assert response.status_code == HTTPStatus.OK
    return response.json()["items"]


@pytest.mark.usefixtures("prepare_users_data")
class TestShowUsers:
    def test_show_user(self, app_url, prepare_users_data):
        user_id = prepare_users_data[-1]
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


class TestShowNonExistentUsers:
    @pytest.mark.parametrize("user_id", [13])
    def test_show_nonexistent_user(self, app_url: str, user_id: int):
        response = requests.get(f"{app_url}/api/users/{user_id}")

        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
    def test_show_user_with_invalid_id(self, app_url: str, user_id: int):
        response = requests.get(f"{app_url}/api/users/{user_id}")

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.usefixtures("prepare_users_data")
class TestUsersPagination:
    def test_check_users_total(self, app_url: str):
        response = requests.get(f"{app_url}/api/users")

        result = response.json()

        assert response.status_code == HTTPStatus.OK
        assert result["page"] == 1
        assert result["size"] == 10
        assert len(result["items"]) == 10
        assert result["total"] == 50

    def test_paginate_users(self, app_url: str):
        response = requests.get(
            f"{app_url}/api/users",
            params={"page": 2},
        )

        result = response.json()

        assert response.status_code == HTTPStatus.OK
        assert result["page"] == 2
        assert result["size"] == 10
        assert len(result["items"]) == 10
        assert result["total"] == 50

    def test_change_users_size_per_page(self, app_url: str):
        response = requests.get(
            f"{app_url}/api/users",
            params={"size": 2},
        )

        result = response.json()

        assert response.status_code == HTTPStatus.OK
        assert result["page"] == 1
        assert result["size"] == 2
        assert len(result["items"]) == 2
        assert result["total"] == 50

    def test_check_invalid_users_page_min_boundary(self, app_url: str):
        response = requests.get(
            f"{app_url}/api/users",
            params={"page": 0},
        )

        result = response.json()

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert (
            result["detail"][0]["msg"]
            == "Input should be greater than or equal to 1"
        )

    def test_check_invalid_users_page_max_boundary(self, app_url: str):
        response = requests.get(
            f"{app_url}/api/users",
            params={"page": 6},
        )

        result = response.json()

        assert response.status_code == HTTPStatus.OK
        assert len(result["items"]) == 0

    def test_check_invalid_users_page_min_boundary_size(self, app_url: str):
        response = requests.get(
            f"{app_url}/api/users",
            params={"size": 0},
        )

        result = response.json()

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert (
            result["detail"][0]["msg"]
            == "Input should be greater than or equal to 1"
        )

    def test_check_invalid_users_page_max_boundary_size(self, app_url: str):
        response = requests.get(
            f"{app_url}/api/users",
            params={"size": 21},
        )

        result = response.json()

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert (
            result["detail"][0]["msg"]
            == "Input should be less than or equal to 20"
        )
