import json

import pytest


@pytest.fixture(scope="class", autouse=False)
def prepare_users_data(users_service):
    users_service.clear_users()

    with open("app/db/users.json") as f:
        users_json = json.load(f)

    users_list = []

    for user in users_json:
        response = users_service.create_user(user)
        users_list.append(response.json())

    user_ids = [user["id"] for user in users_list]

    yield user_ids

    users_service.clear_users()
