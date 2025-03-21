from datetime import timedelta

import pytest  # noqa F401
from django.utils import timezone

from tests.factories import UserFactory
from tests.utils import NinjaSessionClient


class TestApiAuthLogin:
    url = "/login"

    def test_login_with_username_success(
        self, ninja_session_client: NinjaSessionClient, user_factory: UserFactory
    ) -> None:
        """Tests successful login using username."""

        user = user_factory()
        password = "test_password12345"
        user.set_password(password)
        user.save()

        data = {"login_id": user.username, "password": password}

        response = ninja_session_client.post(self.url, json=data)

        assert response.status_code == 200
        assert "user" in response.json()

        response_data = response.json()
        response_data["user"]["id"] == str(user.id)

        assert response_data["user"]["email"] == user.email
        assert response_data["user"]["username"] == user.username

    def test_login_with_email_success(
        self, ninja_session_client: NinjaSessionClient, user_factory: UserFactory
    ) -> None:
        """Tests successful login using email."""

        user = user_factory()
        password = "test_password12345"
        user.set_password(password)
        user.save()

        data = {"login_id": user.email, "password": password}

        response = ninja_session_client.post(self.url, json=data)

        assert response.status_code == 200

        response_data = response.json()

        assert response_data["user"]["id"] == str(user.id)
        assert response_data["user"]["email"] == user.email

    def test_login_min_password(
        self, ninja_session_client: NinjaSessionClient, user_factory: UserFactory
    ) -> None:
        """Test login with password shorter than expected."""

        user = user_factory()
        password = "_pass"
        user.set_password(password)
        user.save()

        data = {"login_id": user.email, "password": password}

        response = ninja_session_client.post(self.url, json=data)

        assert response.status_code == 422

        response_data = response.json()

        assert (
            response_data["detail"][0]["msg"]
            == "String should have at least 10 characters"
        )
        assert response_data["detail"][0]["ctx"]["min_length"] == 10

    def test_login_wrong_password(
        self, ninja_session_client: NinjaSessionClient, user_factory: UserFactory
    ) -> None:
        """Test login with incorrect password."""

        user = user_factory()
        password1 = "test_pass12345"
        user.set_password(password1)
        user.save()

        password2 = "testpassword12345"
        data = {"login_id": user.email, "password": password2}

        response = ninja_session_client.post(self.url, json=data)

        assert response.status_code == 401

        response_data = response.json()

        assert response_data["message"] == "Invalid credentials."
        assert response_data["detail"] == "Username/Email or password is incorrect."

    def test_login_fails_with_non_lowercase_email(
        self, ninja_session_client: NinjaSessionClient, user_factory: UserFactory
    ) -> None:
        """Test that login fails when the email is not in lowercase."""

        user = user_factory()
        password = "test_password12345"
        user.set_password(password)
        user.save()

        data = {"login_id": user.email.upper(), "password": password}

        response = ninja_session_client.post(self.url, json=data)

        assert response.status_code == 401

        response_data = response.json()

        assert response_data["message"] == "Invalid credentials."
        assert response_data["detail"] == "Username/Email or password is incorrect."

    def test_login_with_username_case_insensitive(
        self, ninja_session_client: NinjaSessionClient, user_factory: UserFactory
    ) -> None:
        """Test login using case insensitive username."""

        user = user_factory()
        password = "test_password121345"
        user.set_password(password)
        user.save()

        data = {"login_id": user.username.upper(), "password": password}

        response = ninja_session_client.post(self.url, json=data)

        assert response.status_code == 401

        response_data = response.json()

        assert response_data["message"] == "Invalid credentials."
        assert response_data["detail"] == "Username/Email or password is incorrect."

    def test_login_nonexistent_user(
        self, ninja_session_client: NinjaSessionClient, user_factory: UserFactory
    ) -> None:
        """Test login with non-existent user."""

        data = {"login_id": "UserNonExistent", "password": "test_password12345"}

        response = ninja_session_client.post(self.url, json=data)

        assert response.status_code == 401

        response_data = response.json()

        assert response_data["message"] == "Invalid credentials."
        assert response_data["detail"] == "Username/Email or password is incorrect."

    def test_login_empty_username_field(
        self, ninja_session_client: NinjaSessionClient, user_factory: UserFactory
    ) -> None:
        """Test login with empty username field."""

        user = user_factory()
        password = "test_password121345"
        user.set_password(password)
        user.save()

        data = {"login_id": "", "password": password}

        response = ninja_session_client.post(self.url, json=data)

        assert response.status_code == 422

        response_data = response.json()

        assert (
            response_data["detail"][0]["msg"]
            == "Value error, The login_id field cannot be empty."
        )

    def test_account_lockout_after_failed_attempts(
        self, ninja_session_client: NinjaSessionClient, user_factory: UserFactory
    ) -> None:
        """Test account lockout after multiple failed attempts."""

        user = user_factory()
        password = "test_password12345"
        user.set_password(password)
        user.save()

        data = {"login_id": user.username, "password": "wrong_password12345"}

        for _ in range(5):
            response = ninja_session_client.post(self.url, json=data)
            assert response.status_code == 401

            response_data = response.json()

            assert response_data["message"] == "Invalid credentials."
            assert response_data["detail"] == "Username/Email or password is incorrect."

        response = ninja_session_client.post(self.url, json=data)
        assert response.status_code == 429

        response_data = response.json()
        assert response_data["message"] == "Too many login attempts"
        assert (
            response_data["detail"]
            == "Account temporarily locked for security reasons."
        )

    def test_login_with_locked_account(
        self, ninja_session_client: NinjaSessionClient, user_factory: UserFactory
    ) -> None:
        """Login test with locked account."""

        user = user_factory()
        password = "test_password12345"
        user.set_password(password)
        user.account_locked_until = timezone.now() + timedelta(minutes=30)
        user.save()

        data = {"login_id": user.username, "password": password}

        response = ninja_session_client.post(self.url, json=data)

        assert response.status_code == 403

        response_data = response.json()

        assert response_data["message"] == "Account temporarily locked."
        assert (
            response_data["detail"]
            == f"Please try again after {user.account_locked_until.strftime('%H:%M:%S')}"
        )

    def test_login_resets_failed_attempts(
        self, ninja_session_client: NinjaSessionClient, user_factory: UserFactory
    ) -> None:
        """tests whether successful login resets the failed attempts counter."""

        user = user_factory()
        password = "test_password12345"
        user.set_password(password)
        user.failed_login_attempts = 2
        user.last_failed_login = timezone.now()
        user.save()

        data = {"login_id": user.username, "password": password}

        response = ninja_session_client.post(self.url, json=data)

        assert response.status_code == 200

        updater_user = user.__class__.objects.get(id=user.id)

        assert updater_user.failed_login_attempts == 0
        assert updater_user.last_failed_login is None

    def test_login_after_lock_expires(
        self, ninja_session_client: NinjaSessionClient, user_factory: UserFactory
    ) -> None:
        """Tests login after lockout period expires."""

        user = user_factory()
        password = "test_password12345"
        user.set_password(password)
        user.account_locked_until = timezone.now() - timedelta(minutes=10)
        user.save()

        data = {"login_id": user.username, "password": password}

        response = ninja_session_client.post(self.url, json=data)

        assert response.status_code == 200

        response_data = response.json()

        assert response_data["user"]["id"] == str(user.id)
        assert response_data["user"]["email"] == user.email
