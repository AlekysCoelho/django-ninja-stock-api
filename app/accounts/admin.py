from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, User
from django.utils.translation import gettext_lazy as _

from app.accounts.forms import UserChangeForm, UserCreationForm

UserModel = get_user_model()


class CustomAdminAuthenticationForm(AdminAuthenticationForm):
    """
    Custom admin authentication form that shows a specific error message
    for superusers trying to login with username instead of email.
    """

    error_messages = {
        **AdminAuthenticationForm.error_messages,
        "invalid_login": _(
            "Please enter the correct email and password for a staff "
            "account. Note that both fields may be case-sensitive."
        ),
    }


class CustomAdminSite(AdminSite):
    site_header = "Stock Admin Area"
    site_title = "Stock Admin"
    index_title = "Stock Administration"
    login_template = "accounts/admin/login.html"
    login_form = CustomAdminAuthenticationForm


admin_site = CustomAdminSite()


@admin.register(UserModel, site=admin_site)
class UserAdmin(auth_admin.UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    model = User
    list_display = [
        "username",
        "email",
        "failed_login_attempts",
        "last_failed_login",
        "account_locked_until",
    ]
    fieldsets = auth_admin.UserAdmin.fieldsets + (
        (
            _("Security info"),
            {
                "fields": (
                    "failed_login_attempts",
                    "last_failed_login",
                    "account_locked_until",
                ),
                "classes": _(
                    "collapse",
                ),
            },
        ),
        (
            _("Personal info"),
            {"fields": ("bio",)},
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "usable_password", "password1", "password2"),
            },
        ),
    )
    readonly_fields = [
        "failed_login_attempts",
        "last_failed_login",
        "account_locked_until",
    ]
    search_fields = ["username", "email"]
    ordering = ["date_joined"]


admin_site.register(Group)
