import pytest
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.db.utils import IntegrityError
from django.http import HttpRequest
from django.test import RequestFactory

from app.accounts.backends import EmailOrUsernameModelBackend
from app.accounts.models import User
from tests.factories import SuperUserFactory, UserFactory

authenticate_backend = EmailOrUsernameModelBackend()


class TestUser:
    def test_create_user(self, new_user: User, db):
        """Test creating a new user."""
        assert new_user.username
        assert new_user.email
        assert isinstance(new_user, User)

    def test_email_uniqueness(self, user_factory: UserFactory, db):
        """Test that email addresses are unique."""
        user_factory(email="user1@example.com")
        user2 = user_factory.build(
            email="user1@example.com"
        )  # build to avoid saving to the db
        with pytest.raises(IntegrityError) as execinfo:
            user2.save()
        assert "UNIQUE constraint failed: stock_users.email" in str(execinfo.value)

    def test_user_str(self, new_user: User):
        """Test the string representation of a user."""
        assert str(new_user) == new_user.username

    def test_create_multiple_users(self, user_factory: UserFactory, db):
        """Test creating multiple users."""
        users = user_factory.create_batch(5)
        assert len(users) == 5
        assert all(isinstance(user, User) for user in users)

    def test_common_user_login_with_username(
        self, request: HttpRequest, user_factory: UserFactory, db
    ):
        """Test that a common user can log in with username."""
        password = "password123"
        user = user_factory(username="commonuser", password=password)
        authenticated_user = authenticate_backend.authenticate(
            request=request, username="commonuser", password=password
        )
        assert authenticated_user is not None
        assert authenticated_user == user

    def test_common_user_login_with_email(
        self, request: HttpRequest, user_factory: UserFactory, db
    ):
        """Test that a common user can log in with email."""

        password = "password123"

        user = user_factory(
            username="testuser",
            email="commonuser@example.com",
            password=password,
            is_active=True,
        )

        authenticated_user = authenticate_backend.authenticate(
            request=request,
            username="commonuser@example.com",
            password=password,
        )

        assert authenticated_user is not None
        assert authenticated_user == user

    def test_superuser_login_with_email(
        self, request: HttpRequest, super_user_factory: SuperUserFactory, db
    ):
        """Test that a superuser can only log in with email."""
        # cache.clear()
        password = "password123"

        superuser = super_user_factory(
            username="testuser",
            email="superuser@example.com",
            password=password,
            is_superuser=True,
        )

        # Debug para verificar o usuário criado
        print("\n=== User Debug ===")
        print(f"Username: {superuser.username}")
        print(f"Email: {superuser.email}")
        print(f"Is active: {superuser.is_active}")

        authenticated_superuser = authenticate_backend.authenticate(
            request=request,
            username="superuser@example.com",
            password=password,
        )

        assert authenticated_superuser is not None
        assert authenticated_superuser == superuser

    def test_superuser_login_with_username_fails(
        self, super_user_factory: SuperUserFactory, db
    ):
        """Test that a superuser cannot log in with username."""
        password = "password123"
        superuser = super_user_factory(
            username="superuser",
            email="superuser@example.com",
            password=password,
            is_superuser=True,
        )

        # Debug para verificar o usuário criado
        print("\n=== User Debug ===")
        print(f"Username: {superuser.username}")
        print(f"Email: {superuser.email}")
        print(f"Is active: {superuser.is_active}")

        factory = RequestFactory()
        request = factory.get("/")
        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)
        request.session.save()  # save the session

        authenticated_superuser = authenticate_backend.authenticate(
            request=request,
            username="superuser",
            password=password,
        )
        assert authenticated_superuser is None
