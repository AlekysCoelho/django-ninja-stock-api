import pytest
from django.conf import settings
from pytest_factoryboy import register

from app.accounts.api import auth_router
from tests.factories import SuperUserFactory, UserFactory
from tests.utils import NinjaSessionClient

register(UserFactory)
register(SuperUserFactory)


@pytest.fixture(scope="session")
def django_db_setup():
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "test_django_db",
        "NAME": "test_djangodb",
        "PASSWORD": "TestDjangoDB",
        "USER": "test_django",
        "PORT": 5432,
    }


@pytest.fixture
def new_user(db, user_factory):
    return user_factory()


@pytest.fixture
def new_super_user(db, super_user_factory):
    return super_user_factory()


@pytest.fixture
def ninja_session_client(db):
    """Fixture that provides a Django Ninja client with session suport."""
    return NinjaSessionClient(auth_router)


@pytest.fixture
def authenticated_client(ninja_session_client, user_factory):
    """Fixture that provides an authenticated client with a user."""
    user = user_factory()
    user.set_password("test_password12345")
    user.save()

    response = ninja_session_client.post(
        "/login", json={"login_id": user.username, "password": "test_password12345"}
    )

    assert response.status_code == 200, f"Invalid credentials: {response.json()}"
    print(f"AUTHENTICATED CLIENT == {response.status_code}")
    return ninja_session_client, user
