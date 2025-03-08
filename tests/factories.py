import logging

import factory

# from app.accounts.models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from faker import Faker

from app.logs import get_logger

User = get_user_model()
faker = Faker()


test_logger = get_logger("test", logging.WARNING)


class BaseUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        abstract = True
        django_get_or_create = (
            "username",
            "email",
        )

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.password = make_password(extracted or "password123")
        if create:
            self.save()


class UserFactory(BaseUserFactory):
    is_staff = False
    is_superuser = False


class SuperUserFactory(BaseUserFactory):
    is_staff = True
    is_superuser = True
