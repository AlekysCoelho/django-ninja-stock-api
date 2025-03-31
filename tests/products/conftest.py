import pytest
from pytest_factoryboy import register

from tests.products.factories import DiscountProductFactory, NoDiscountProductFactory

register(NoDiscountProductFactory)
register(DiscountProductFactory)


@pytest.fixture
def new_product(db, product_factory):
    return product_factory()


@pytest.fixture
def no_discount_product(db, no_discount_product_factory):
    return no_discount_product_factory()


@pytest.fixture
def discount_product(db, discount_product_factory):
    return discount_product_factory()
