from http import HTTPStatus

import pytest

from app.models.user import User, UserCreate, fake
from app.utils import fake_link


@pytest.fixture(autouse=False)
def users_items(users_service):
    response = users_service.get_users()
    assert response.status_code == HTTPStatus.OK
    return response.json()["items"]


@pytest.fixture(autouse=False)
def created_user(users_service):
    user = UserCreate.random()
    response = users_service.create_user(user.model_dump())
    return User(**response.json())


class TestUsersCreating:
    def test_create_user(self, users_service):
        user = UserCreate.random()

        response = users_service.create_user(user.model_dump())

        assert response.status_code == HTTPStatus.CREATED
        response_json = response.json()
        assert response_json["id"] is not None
        assert response_json["first_name"] == user.first_name
        assert response_json["last_name"] == user.last_name
        assert response_json["avatar"] == user.avatar
        assert response_json["email"] == user.email
        _ = User.model_validate(response_json)

    def test_create_user_without_first_name(self, users_service):
        user = {
            "email": fake.email(),
            "last_name": fake.last_name(),
            "avatar": fake_link(),
        }

        response = users_service.create_user(user)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        detail = response.json()["detail"][0]
        assert detail["loc"] == ["body", "first_name"]
        assert detail["msg"] == "Field required"


@pytest.mark.usefixtures("prepare_users_data")
class TestShowUsers:
    def test_show_user(self, users_service, prepare_users_data):
        user_id = prepare_users_data[-1]

        response = users_service.get_user(user_id)
        user = response.json()

        assert response.status_code == HTTPStatus.OK
        _ = User.model_validate(user)

    def test_show_just_created_user(self, users_service, created_user: str):
        response = users_service.get_user(created_user.id)

        assert response.status_code == HTTPStatus.OK
        response_json = response.json()
        assert response_json["id"] == created_user.id
        assert response_json["first_name"] == created_user.first_name
        assert response_json["last_name"] == created_user.last_name
        assert response_json["avatar"] == created_user.avatar
        assert response_json["email"] == created_user.email
        _ = User.model_validate(response_json)

    def test_show_users(self, users_service):
        response = users_service.get_users()

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
    def test_show_nonexistent_user(self, users_service, user_id: int):
        response = users_service.get_user(user_id)

        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("user_id", [-1, 0, "fafaf"])
    def test_show_user_with_invalid_id(self, users_service, user_id: int):
        response = users_service.get_user(user_id)

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestUserUpdating:
    def test_partial_update_user(self, users_service, created_user):
        new_first_name = fake.first_name()

        response = users_service.update_user(
            created_user.id,
            json_={"first_name": new_first_name},
        )

        assert response.status_code == HTTPStatus.OK
        response_json = response.json()
        assert response_json["id"] == created_user.id
        assert response_json["first_name"] == new_first_name
        assert response_json["last_name"] == created_user.last_name
        assert response_json["avatar"] == created_user.avatar
        assert response_json["email"] == created_user.email
        _ = User.model_validate(response_json)

    def test_update_all_user_info(self, users_service, created_user):
        new_user_info = UserCreate.random()

        response = users_service.update_user(
            created_user.id,
            json_=new_user_info.model_dump(),
        )

        assert response.status_code == HTTPStatus.OK
        response_json = response.json()
        assert response_json["id"] == created_user.id
        assert response_json["first_name"] == new_user_info.first_name
        assert response_json["last_name"] == new_user_info.last_name
        assert response_json["avatar"] == new_user_info.avatar
        assert response_json["email"] == new_user_info.email
        _ = User.model_validate(response_json)

    def test_update_user_with_invalid_id(self, users_service):
        new_user_info = UserCreate.random()
        users_service.clear_users()

        response = users_service.update_user(
            f"{fake.random_int(min=10, max=100)}",
            json_=new_user_info.model_dump(),
        )

        assert response.status_code == HTTPStatus.NOT_FOUND
        response_json = response.json()["detail"] == "User not found"


def test_delete_user(users_service, created_user):
    response = users_service.delete_user(created_user.id)

    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == "User deleted"

    # AND WHEN
    get_user_response = users_service.get_user(created_user.id)

    # AND THEN
    assert get_user_response.status_code == HTTPStatus.NOT_FOUND
    assert get_user_response.json()["detail"] == "User not found"


@pytest.mark.usefixtures("prepare_users_data")
class TestUsersPagination:
    def test_check_users_total(self, users_service, prepare_users_data):
        response = users_service.get_users()

        result = response.json()

        assert response.status_code == HTTPStatus.OK
        assert result["page"] == 1
        assert result["size"] == 10
        assert len(result["items"]) == 10
        assert result["total"] == 50

    def test_paginate_users(self, users_service):
        response = users_service.get_users(page=2)

        result = response.json()

        assert response.status_code == HTTPStatus.OK
        assert result["page"] == 2
        assert result["size"] == 10
        assert len(result["items"]) == 10
        assert result["total"] == 50

    def test_change_users_size_per_page(self, users_service):
        response = users_service.get_users(size=2)

        result = response.json()

        assert response.status_code == HTTPStatus.OK
        assert result["page"] == 1
        assert result["size"] == 2
        assert len(result["items"]) == 2
        assert result["total"] == 50

    def test_check_invalid_users_page_min_boundary(self, users_service):
        response = users_service.get_users(page=0)

        result = response.json()

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert (
            result["detail"][0]["msg"]
            == "Input should be greater than or equal to 1"
        )

    def test_check_invalid_users_page_max_boundary(self, users_service):
        response = users_service.get_users(page=6)

        result = response.json()

        assert response.status_code == HTTPStatus.OK
        assert len(result["items"]) == 0

    def test_check_invalid_users_page_min_boundary_size(self, users_service):
        response = users_service.get_users(size=0)

        result = response.json()

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert (
            result["detail"][0]["msg"]
            == "Input should be greater than or equal to 1"
        )

    def test_check_invalid_users_page_max_boundary_size(self, users_service):
        response = users_service.get_users(size=21)

        result = response.json()

        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert (
            result["detail"][0]["msg"]
            == "Input should be less than or equal to 20"
        )
