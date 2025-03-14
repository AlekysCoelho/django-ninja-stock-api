from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db import transaction
from django.dispatch import receiver
from django.http import HttpRequest
from django.utils import timezone

from app.accounts.models import User as UserModel
from app.logs import get_logger

User = get_user_model()
security_logger = get_logger("security")


@receiver(user_logged_in)
def user_logged_handler(
    sender, request: HttpRequest, user: UserModel, **kwargs
) -> None:
    """
    Records successful login and resets fail counters.

    Args:
        sender: Signal sender
        request: The HTTP request
        user: The user that successfully logged in
        kwargs: Additional arguments
    """
    with transaction.atomic():
        if user.failed_login_attemps > 0:
            user.failed_login_attemps = 0
            user.last_failed_login = None
            user.account_locked_until = None
            user.save(
                update_fields=[
                    "failed_login_attemps",
                    "last_failed_login",
                    "account_locked_until",
                ]
            )

        # IP AND USER_AGENT registration
        ip = request.META.get("REMOTE_ADDR", "")
        user_agent = request.META.get("HTTP_USER_AGENT", "")

        security_logger.info(
            f"Login success: {user.username} | IP: {ip} | User-Agent: {user_agent}",
            extra={"username": user.username, "ip": ip, "user_agent": user_agent},
        )


@receiver(user_login_failed)
def user_login_failed_handler(
    sender, credentials, request: HttpRequest, **kwargs
) -> None:
    """
    Controls login failures to prevent brute force attacks.

    Args:
        sender: Signal sender
        credentials: Login credentials
        request: The HTTP request
        kwargs: Additional arguments
    """
    username = credentials.get("username", "")
    ip = request.META.get("REMOTE_ADDR", "") if request else "N/A"
    user_agent = request.META.get("HTTP_USER_AGENT", "") if request else "N/A"

    security_logger.warning(
        f"Login failed: {username} | IP: {ip} | User-Agent: {user_agent}",
        extra={"username": username, "ip": ip, "user_agent": user_agent},
    )

    try:
        with transaction.atomic():
            user = (
                User.objects.get(email=username)
                if "@" in username
                else User.objects.get(username=username)
            )

            # Increment failure counter
            user.failed_login_attemps += 1
            user.last_failed_login = timezone.now()

            # Implements temporary blocking after multiple attempts
            if user.failed_login_attemps >= 5:
                lock_minutes = min(30, 5 * (user.failed_login_attemps - 4))
                user.account_locked_until = timezone.now() + timezone.timedelta(
                    minutes=lock_minutes
                )
                security_logger.warning(
                    f"Account temporarily blocked: {username} for {lock_minutes} minutes",
                    extra={"username": username, "lock_minutes": lock_minutes},
                )

            user.save(
                update_fields=[
                    "failed_login_attemps",
                    "last_failed_login",
                    "account_locked_until",
                ]
            )

    except User.DoesNotExist:
        security_logger.warning(
            f"Login attempt with non-existent user: {username}",
            extra={"username": username, "ip": ip, "user_agent": user_agent},
        )
