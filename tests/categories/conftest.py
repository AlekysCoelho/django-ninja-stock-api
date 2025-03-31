import pytest
from pytest_factoryboy import register

from tests.categories.factories import CategoryFactory

register(CategoryFactory)


@pytest.fixture
def new_category(db, category_factory):
    return category_factory()
