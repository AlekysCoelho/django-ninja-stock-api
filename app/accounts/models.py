import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_email
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bio = models.TextField(blank=True)
    email = models.EmailField(
        _("email address"),
        unique=True,
        validators=[validate_email],
        error_messages={"unique": _("User with this email already exists.")},
    )
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "stock_users"
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-username"]

    def __str__(self) -> str:
        return f"{self.username}"

    def save(self, *args, **kwargs) -> None:
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)
