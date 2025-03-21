from xml.dom import ValidationErr

from django.contrib import auth
from django.contrib.auth import authenticate, get_user_model
from django.db.models import Q
from django.utils import timezone
from ninja import Router

from app.accounts.schemas import LoginInputSchema, LoginResponseSchema, MessageSchema

User = get_user_model()
auth_router = Router()


@auth_router.post(
    "login",
    response={
        200: LoginResponseSchema,
        401: MessageSchema,
        403: MessageSchema,
        429: MessageSchema,
        500: MessageSchema,
    },
    url_name="auth-login",
)
def auth_login(request, login_data: LoginInputSchema):  # noqa PLR0911
    """
    Endpoint for user authentication using email or useranme.

    Allow login with email or username, checks login attempts and account lockout.
    """
    try:
        user = User.objects.filter(
            Q(email__iexact=login_data.login_id)
            | Q(username__iexact=login_data.login_id)
        ).first()

        if not user:
            return (
                401,
                {
                    "message": "Invalid credentials.",
                    "detail": "Username/Email or password is incorrect.",
                },
            )

        if user and user.account_locked_until:
            if user.account_locked_until > timezone.now():
                return (
                    403,
                    {
                        "message": "Account temporarily locked.",
                        "detail": f"Please try again after {user.account_locked_until.strftime('%H:%M:%S')}",
                    },
                )

        if user:

            if user.failed_login_attempts >= 5:
                user.account_locked_until = timezone.now() + timezone.timedelta(
                    minutes=5
                )
                user.save(
                    update_fields=[
                        "failed_login_attempts",
                        "last_failed_login",
                        "account_locked_until",
                    ]
                )

                return (
                    429,
                    {
                        "message": "Too many login attempts",
                        "detail": "Account temporarily locked for security reasons.",
                    },
                )

            user.save(update_fields=["failed_login_attempts", "last_failed_login"])

        authenticated_user = authenticate(
            request,
            username=login_data.login_id,
            password=login_data.password,
        )

        if authenticated_user:
            if authenticated_user.failed_login_attempts > 0:
                authenticated_user.failed_login_attempts = 0
                authenticated_user.last_failed_login = None
                authenticated_user.save(
                    update_fields=["failed_login_attempts", "last_failed_login"]
                )

            # Check if the session is available.
            if hasattr(request, "session"):
                auth.login(request, authenticated_user)
            else:
                print("SESSÃO INDISPONÍVEL")

            return 200, {
                "message": "Login successful.",
                "user": authenticated_user,
                "detail": None,
            }
        else:
            return (
                401,
                {
                    "message": "Invalid credentials.",
                    "detail": "Username/Email or password is incorrect.",
                },
            )

    except ValidationErr as err:
        return (400, {"message": "Validation error.", "detail": str(err)})
    except Exception as err:
        return (500, {"message": "Internal server error.", "detail": str(err)})


@auth_router.get("get-csrftoken", response={200: MessageSchema, 401: MessageSchema})
def csrf_test(request):
    return 200, {"message": "CRSF TOKEN"}
