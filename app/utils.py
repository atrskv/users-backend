from faker import Faker
from fastapi.params import Query
from fastapi_pagination import Params


def get_pagination_params(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=10, ge=1, le=20),
) -> Params:
    return Params(page=page, size=size)


def fake_link():
    return f"https://{''.join(Faker().words(2))}.com"
