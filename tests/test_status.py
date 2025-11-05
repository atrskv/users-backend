from http import HTTPStatus

import requests


def test_app_health_check_users_is_not_empty(app_url: str, prepare_users_data):
    response = requests.get(f"{app_url}/api/status")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["users"] is True


def test_app_health_check_users_is_empty(app_url: str, clear_users_data):
    response = requests.get(f"{app_url}/api/status")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["users"] is False
