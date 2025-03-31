import pytest


class TestCategory:
    def test_create_category(self, new_category, db) -> None:
        """Test creating a new category."""

        assert new_category.name
        assert new_category.description
        assert new_category.id is not None

    def test_return_number_products_in_the_category(
        self, new_category, product_factory, db
    ) -> None:
        """Tests the count of products in a category."""

        products = [product_factory(category=new_category) for _ in range(5)]

        assert new_category.get_products.count() == 5
