import factory

from app.categories.models import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ("name",)

    name = factory.Sequence(lambda n: f"category{n}")
    description = factory.Faker("text")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower())
    is_active = True
