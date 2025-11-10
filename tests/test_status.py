from http import HTTPStatus

import requests


def test_app_health_check_database(app_url: str):
    response = requests.get(f"{app_url}/api/status")

    assert response.status_code == HTTPStatus.OK
    assert response.json()["database"] is True, "database is down"
