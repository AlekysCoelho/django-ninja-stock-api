import pytest
from pytest_factoryboy import register

from app.products.tests.factories import CategoryFactory

register(CategoryFactory)


@pytest.fixture
def new_category(db, category_factory):
    return category_factory()
