import os

import dotenv
import pytest
import requests


@pytest.fixture(autouse=True)
def load_env():
    _ = dotenv.load_dotenv()


@pytest.fixture(autouse=False)
def app_url():
    return os.getenv("APP_URL")


@pytest.fixture(autouse=False)
def prepare_users_data(app_url: str):
    _ = requests.post(f"{app_url}/api/users")


@pytest.fixture(autouse=False)
def clear_users_data(app_url: str):
    _ = requests.delete(f"{app_url}/api/users")
