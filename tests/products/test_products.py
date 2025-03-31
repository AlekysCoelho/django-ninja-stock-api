from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from app.products.models import Product
from app.products.tests.factories import (
    DiscountProductFactory,
    NoDiscountProductFactory,
    ProductFactory,
)


class TestProduct:
    def test_create_product_successfuly_no_discount(
        self, no_discount_product: NoDiscountProductFactory, db
    ) -> None:
        """Test creating a new product without discount."""

        assert no_discount_product.name
        assert no_discount_product.description
        assert no_discount_product.category
        assert no_discount_product.price > 0
        assert no_discount_product.price > 0
        assert no_discount_product.stock >= 0
        assert isinstance(no_discount_product, Product)
        assert no_discount_product.final_price == no_discount_product.price

    def test_create_product_successfuly_with_discount(
        self, discount_product: DiscountProductFactory, db
    ) -> None:
        """Test creating a new product with discount."""

        assert discount_product.name
        assert discount_product.description
        assert discount_product.category
        assert discount_product.price > 0
        assert discount_product.stock >= 0
        assert isinstance(discount_product, Product)
        assert discount_product.final_price is not None

        expected_final_price = discount_product.price * (
            Decimal("1") - (discount_product.discount / Decimal("100"))
        )

        assert discount_product.final_price == expected_final_price
        assert discount_product.final_price < discount_product.price

    def test_create_product_with_invalid_price(
        self, product_factory: ProductFactory, db
    ) -> None:
        """Test creating a new product with invalid price."""

        with pytest.raises(ValidationError, match="Price must be greater than zero."):
            product_factory(price=0).full_clean()
        with pytest.raises(ValidationError, match="Price must be greater than zero."):
            product_factory(price=-1).full_clean()

    def test_create_product_with_invalid_discount(
        self, product_factory: ProductFactory, db
    ) -> None:
        """Test creating a new product with invalid discount."""

        with pytest.raises(
            ValidationError, match="Discount must be greater than or equal to zero."
        ):
            product_factory(discount=-10).full_clean()
        with pytest.raises(
            ValidationError, match="Discount must be less than or equal to 100."
        ):
            product_factory(discount=150).full_clean()

    def test_create_product_with_invalid_stock(
        self, product_factory: ProductFactory, db
    ) -> None:
        """Test creating a new product with invalid stock."""

        with pytest.raises(
            ValidationError, match="Stock must be greater than or equal to zero."
        ):
            product_factory(stock=-5)
