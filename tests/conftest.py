import json
import os

import dotenv
import pytest
import requests


@pytest.fixture(scope="session", autouse=True)
def load_env():
    _ = dotenv.load_dotenv()


@pytest.fixture(scope="session", autouse=False)
def app_url():
    return os.getenv("APP_URL")


@pytest.fixture(scope="class", autouse=False)
def prepare_users_data(app_url: str):
    _ = requests.post(f"{app_url}/api/users")

    with open("app/db/users.json") as f:
        users_json = json.load(f)

    users_list = []

    for user in users_json:
        response = requests.post(f"{app_url}/api/users/", json=user)
        users_list.append(response.json())

    user_ids = [user["id"] for user in users_list]

    yield user_ids

    for user_id in user_ids:
        requests.delete(f"{app_url}/api/users/{user_id}")
