import re
from typing import Optional, Type

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.messages import constants
from django.core.cache import cache
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from app.accounts.models import User as CustomUser
from app.logs import get_logger

security_logger = get_logger("security")
info_logger = get_logger("test")

User = get_user_model()


class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authentication backend that allows login with username or email.
    Super users can only login with email.
    """

    EMAIL_REGEX = re.compile(
        r"^(?=.{3,254}$)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )

    def is_valid_email(self, email: str) -> bool:
        """
        Validates an email address by ensuring that it follows a secure format.
        """
        if not isinstance(email, str):
            return False

        if len(email) > 254:
            return False

        if not self.EMAIL_REGEX.match(email):
            return False

        return True

    def _increment_login_attempts(self, username: str) -> None:
        """Increment failed attempt counter"""
        if not username:
            return

        username_lower = username.lower()
        key = f"login_attempts:{username_lower}"

        attempts = cache.get(key, 0)
        cache.set(key, attempts + 1, 60 * 15)

    def authenticate(
        self, request: HttpRequest, username: str = None, password: str = None, **kwargs
    ) -> Optional[Type[CustomUser]]:
        """Check credentials for user login with email or username"""
        if not username or not password:
            return None

        info_logger.info(f"Attempting authentication with username/email: {username}")

        is_email = self.is_valid_email(username)
        login_type = "email" if is_email else "username"

        try:
            # Check if there is a superuser trying to log in with username
            if not is_email:
                # Check if there is a superuser with this username
                try:
                    potential_superuser = User.objects.get(username=username)
                    if potential_superuser.is_superuser:
                        if request:
                            messages.add_message(
                                request,
                                constants.ERROR,
                                _(
                                    "Administrators must log in using their email address."
                                ),
                            )
                            return None
                        security_logger.warning(
                            f"Invalid login attempt for superuser using username: {username}",
                            extra={"request": request, "type": "auth_violation"},
                        )
                        return None
                except User.DoesNotExist:
                    pass

            if is_email:
                user = User.objects.get(email=username)
            else:
                user = User.objects.get(username=username)

            if user.check_password(password):
                security_logger.info(
                    f"Successful login via {login_type} for user {user.username}",
                    extra={
                        "request": request,
                        "username": user.username,
                        "type": "login_success",
                    },
                )
                return user
            else:
                security_logger.info(
                    f"Invalid password for login via {login_type}: {username}",
                    extra={
                        "request": request,
                        "type": "login_failure",
                    },
                )
        except User.DoesNotExist:
            security_logger.warning(
                f"Login attempt for non-existent user via {login_type}: {username}",
                extra={
                    "request": request,
                    "type": "login_failure",
                },
            )

        # Still increment attempts to prevent user enumeration
        self._increment_login_attempts(username)

        return None

    def get_user(self, user_id):
        """
        Retrieve user by ID and ensure proper permissions are loaded
        """
        try:
            user = User.objects.get(pk=user_id)
            return user
        except User.DoesNotExist:
            return None
