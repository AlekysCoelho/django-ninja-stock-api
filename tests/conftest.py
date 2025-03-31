import pytest
from pytest_factoryboy import register

from tests.products.factories import ProductFactory

register(ProductFactory)


@pytest.fixture
def new_product(db, product_factory):
    return product_factory()
