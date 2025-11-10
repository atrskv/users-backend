from http import HTTPStatus

from fastapi import APIRouter

from app.db.engine import check_availability
from app.models.status import AppStatus

router = APIRouter()


@router.get("/api/status", status_code=HTTPStatus.OK)
def get_status() -> AppStatus:
    return AppStatus(database=check_availability())
