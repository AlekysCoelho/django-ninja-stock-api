import pytest
from psycopg import IntegrityError

from app.products.models import Category
from app.products.tests.factories import CategoryFactory


class TestCategory:
    def test_create_category(self, new_category: Category, db):
        """Test creating a new category."""

        assert new_category.name
        assert new_category.description
        assert new_category.id is not None

    def test_return_number_products_in_the_category(
        self, new_category, product_factory, db
    ):
        """Tests the count of products in a category."""

        products = [  # noqa F841
            product_factory(category=new_category) for _ in range(5)
        ]  # noqa F841

        assert new_category.get_products_count() == 5

        more_products = [  # noqa F841
            product_factory(category=new_category) for _ in range(6)
        ]

        assert new_category.get_products_count() == 11

    def test_category_with_duplicate_name(
        self, new_category: Category, category_factory: CategoryFactory, db
    ):
        """Test that categories with duplicate name are not allowed."""

        with pytest.raises(IntegrityError):
            category_factory(name=new_category.name)
