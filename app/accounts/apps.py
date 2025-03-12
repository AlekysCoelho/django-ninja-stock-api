from django.apps import AppConfig

from app.logs import get_logger

logger = get_logger("", level=20)


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.accounts"
    verbose_name = "Authentication and Security"

    def ready(self) -> None:
        try:
            import app.accounts.signals  # noqa F401

            logger.info("Accounts security signals registered successfully.")
        except ImportError as err:
            logger.error(f"Failed to register account signals: {err}")
            raise
