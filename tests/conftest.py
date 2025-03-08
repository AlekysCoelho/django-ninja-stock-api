import pytest
from django.conf import settings
from pytest_factoryboy import register

from tests.factories import SuperUserFactory, UserFactory

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
