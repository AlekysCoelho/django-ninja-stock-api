import re

from django.contrib import messages
from django.contrib.messages import constants
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _

from app.logs import get_logger

security_logger = get_logger("security", level=30)


class SecurityHeadersMiddleware:
    """Adds security headers to all HTTP responses."""

    def __init__(self, get_response) -> None:
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)

        response["X-Content-Type-Options"] = "nosniff"
        response["X-Frame-Options"] = "DENY"
        response["X-XSS-Protection"] = "1; mode=block"
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"

        # Content Security Policy
        # csp = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:;"
        # response["Content-Security-Policy"] = csp

        # Clickjacking protection
        response["X-Permitted-Cross-Domain-Policies"] = "none"

        return response


class RequestValidationMiddleware:
    """Validates and sanitizes request inputs."""

    def __init__(self, get_response) -> None:
        self.get_response = get_response
        self.logger = security_logger

    def __call__(self, request: HttpRequest):
        if request.GET:
            for key, value in request.GET.items():
                if self.__contains_suspicious_pattern(value):
                    self.logger.warning(
                        f"Possible attack detected in GET parameters: {key} - {value}",
                        extra={
                            "request": request,
                            "type": "security_violation",
                            "ip": self.__get_client_ip(request),
                            "user_agent": request.headers.get("User-Agent"),
                        },
                    )
                    return HttpResponseForbidden("Forbidden")

        if request.POST:
            for key, value in request.POST.items():
                if key != "password" and self.__contains_suspicious_pattern(value):
                    self.logger.warning(
                        f"Possible attack detected in POST parameters: {key} - {value}",
                        extra={
                            "request": request,
                            "type": "security_violation",
                            "ip": self.__get_client_ip(request),
                            "user_agent": request.headers.get("User-Agent"),
                        },
                    )
                    return HttpResponseForbidden("Forbidden")

        return self.get_response(request)

    def __contains_suspicious_pattern(self, value: str) -> bool:
        """Detects common injection patterns."""
        if not isinstance(value, str):
            value = str(value)

        patterns = [
            r"(?i)<script.*?>",  # XSS
            r"(?i)(?:--|%27|%22)[\s]*$",  # SQL Injection refinado
            r"(?i)(?:union\s+select|exec\s+xp_|system\s*\(|eval\s*\(|rm\s+-rf)",  # More injections
        ]

        return any(re.search(pattern, value) for pattern in patterns)

    def __get_client_ip(self, request: HttpRequest) -> str:
        """Retrieve the client IP address from request headers."""
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "Unknown")


class SuperUserEmailLoginMiddleware:
    """
    Middleware to ensure superusers can only login with email.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/admin/login/" and request.method == "POST":
            username = request.POST.get("username", "")
            from .backends import EmailOrUsernameModelBackend

            backend = EmailOrUsernameModelBackend()

            # Se não é um email e temos um usuário com esse username
            if not backend.is_valid_email(username):
                from django.contrib.auth import get_user_model

                User = get_user_model()
                try:
                    user = User.objects.get(username=username)
                    if user.is_superuser:
                        messages.add_message(
                            request,
                            constants.ERROR,
                            _("Administrators must log in using their email address."),
                        )
                        return redirect("/admin/login/")
                except User.DoesNotExist:
                    pass

        response = self.get_response(request)
        return response
