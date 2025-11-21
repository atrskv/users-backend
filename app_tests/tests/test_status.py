from http import HTTPStatus


def test_app_health_check_database(users_service):
    response = users_service.get_status()

    assert response.status_code == HTTPStatus.OK
    assert response.json()["database"] is True, "database is down"
