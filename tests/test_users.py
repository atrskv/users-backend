from http import HTTPStatus

import pytest
import requests

from app.models.user import User, UserCreate, fake
from app.utils import fake_link


@pytest.fixture(autouse=False)
def users_items(app_url: str):
    response = requests.get(f"{app_url}/api/users")
    assert response.status_code == HTTPStatus.OK
    return response.json()["items"]


@pytest.fixture(autouse=False)
def created_user(app_url: str):
    user = UserCreate.random()
    response = requests.post(f"{app_url}/api/users/", json=user.model_dump())
    return User(**response.json())


class TestUsersCreating:
    def test_create_user(self, app_url: str):
        user = UserCreate.random()

        response = requests.post(f"{app_url}/api/users", json=user.model_dump())

        assert response.status_code == HTTPStatus.CREATED
        response_json = response.json()
        assert response_json["id"] is not None
        assert response_json["first_name"] == user.first_name
        assert response_json["last_name"] == user.last_name
        assert response_json["avatar"] == user.avatar
        assert response_json["email"] == user.email
        _ = User.model_validate(response_json)

    def test_create_user_without_first_name(self, app_url: str):
        user = {
            "email": fake.email(),
            "last_name": fake.last_name(),
            "avatar": fake_link(),
        }

        response = requests.post(f"{app_url}/api/users/", json=user)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        detail = response.json()["detail"][0]
        assert detail["loc"] == ["body", "first_name"]
        assert detail["msg"] == "Field required"


@pytest.mark.usefixtures("prepare_users_data")
class TestShowUsers:
    def test_show_user(self, app_url, prepare_users_data):
        user_id = prepare_users_data[-1]
        response = requests.get(f"{app_url}/api/users/{user_id}")

        user = response.json()

        assert response.status_code == HTTPStatus.OK
        _ = User.model_validate(user)

    def test_show_just_created_user(self, app_url: str, created_user: str):
        response = requests.get(f"{app_url}/api/users/{created_user.id}")

        assert response.status_code == HTTPStatus.OK
        response_json = response.json()
        assert response_json["id"] == created_user.id
        assert response_json["first_name"] == created_user.first_name
        assert response_json["last_name"] == created_user.last_name
        assert response_json["avatar"] == created_user.avatar
        assert response_json["email"] == created_user.email
        _ = User.model_validate(response_json)

    def test_show_users(self, app_url: str):
        response = requests.get(f"{app_url}/api/users/")

        users_page = response.json()
        users_items = users_page["items"]

        assert response.status_code == HTTPStatus.OK
        for user in users_items:
            _ = User.model_validate(user)

    def test_show_no_duplicates_first_page_users(
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


class TestUserUpdating:
    def test_partial_update_user(self, app_url: str, created_user):
        new_first_name = fake.first_name()

        response = requests.patch(
            f"{app_url}/api/users/{created_user.id}",
            json={"first_name": new_first_name},
        )

        assert response.status_code == HTTPStatus.OK
        response_json = response.json()
        assert response_json["id"] == created_user.id
        assert response_json["first_name"] == new_first_name
        assert response_json["last_name"] == created_user.last_name
        assert response_json["avatar"] == created_user.avatar
        assert response_json["email"] == created_user.email
        _ = User.model_validate(response_json)

    def test_update_all_user_info(self, app_url: str, created_user):
        new_user_info = UserCreate.random()

        response = requests.patch(
            f"{app_url}/api/users/{created_user.id}",
            json=new_user_info.model_dump(),
        )

        assert response.status_code == HTTPStatus.OK
        response_json = response.json()
        assert response_json["id"] == created_user.id
        assert response_json["first_name"] == new_user_info.first_name
        assert response_json["last_name"] == new_user_info.last_name
        assert response_json["avatar"] == new_user_info.avatar
        assert response_json["email"] == new_user_info.email
        _ = User.model_validate(response_json)

    def test_update_user_with_invalid_id(self, app_url: str):
        new_user_info = UserCreate.random()
        requests.delete(f"{app_url}/api/users/clear")

        response = requests.patch(
            f"{app_url}/api/users/{fake.random_int(min=10, max=100)}",
            json=new_user_info.model_dump(),
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        response_json = response.json()["detail"] == "User not found"


def test_delete_user(app_url: str, created_user):
    response = requests.delete(
        f"{app_url}/api/users/{created_user.id}",
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "User deleted"

    # AND WHEN
    get_user_response = requests.get(f"{app_url}/api/users/{created_user.id}")

    # AND THEN
    assert get_user_response.status_code == HTTPStatus.NOT_FOUND
    assert get_user_response.json()["detail"] == "User not found"


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
