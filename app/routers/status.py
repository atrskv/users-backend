from http import HTTPStatus

from fastapi import APIRouter

from app.database import users_list
from app.models.status import AppStatus

router = APIRouter()


@router.get("/api/status", status_code=HTTPStatus.OK)
def get_status() -> AppStatus:
    return AppStatus(users=bool(users_list))
