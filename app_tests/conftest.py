import dotenv
import pytest

from app_tests.internal.config import API
from app_tests.internal.services.users import UsersService
from app_tests.internal.session import Session_


@pytest.fixture(scope="session", autouse=True)
def load_env():
    _ = dotenv.load_dotenv()


def pytest_addoption(parser):
    parser.addoption("--env", default="dev")


@pytest.fixture(scope="session")
def env(request):
    return request.config.getoption("--env")


@pytest.fixture(scope="session")
def users_service(env):
    with Session_(base_url=API(env).users_service) as session:
        service = UsersService(session)
        yield service
