import factory
from faker import Faker

from app.products.models import Product
from tests.categories.factories import CategoryFactory

faker = Faker()


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f"Product {n} - {faker.word()}")
    description = factory.LazyFunction(lambda: faker.paragraph(nb_sentences=3))
    category = factory.SubFactory(CategoryFactory)
    price = factory.Faker(
        "pydecimal", left_digits=4, right_digits=2, positive=True, min_value=1
    )
    stock = factory.Faker("pydecimal", left_digits=4, right_digits=2)
    discount = factory.Faker("pydecimal", left_digits=4, right_digits=2)


class NoDiscountProductFactory(ProductFactory):
    discount = 0
    final_price = factory.LazyAttribute(
        lambda x: x.price - (x.price * x.discount / 100)
    )


class DiscountProductFactory(ProductFactory):
    discount = factory.Faker("pydecimal", left_digits=4, right_digits=2)
    final_price = factory.LazyAttribute(
        lambda x: x.price - (x.price * x.discount / 100)
    )
