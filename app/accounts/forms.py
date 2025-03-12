import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AdminUserCreationForm, AuthenticationForm
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserCreationForm(AdminUserCreationForm):
    class Meta(AdminUserCreationForm.Meta):
        model = User
        fields = AdminUserCreationForm.Meta.fields + ("bio",)


class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = User
        fields = ("username", "email", "password", "bio")


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Email or Username"),
        widget=forms.TextInput(
            attrs={
                "autofocus": True,
                "class": "form-control",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "autocomplete": "current-password",
            }
        ),
    )

    error_messages = {
        "invalid_login": _(
            "Please enter a correct %(username)s and password. Please note that both fields are case sensitive."
        ),
        "superuser_email_required": _("Superuser must log in using email."),
        "inactive": _("This account is inactive."),
    }

    def clean(self):
        username = self.cleaned_data.get("username", "").strip()
        password = self.cleaned_data.get("password", "").strip()

        if username and password:
            if len(username) > 254 or len(password) > 50:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )

            try:
                if "@" in username:
                    if not re.match(
                        r"^(?=.{3,254}$)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                        username,
                    ):
                        raise forms.ValidationError(
                            self.error_messages["invalid_login"],
                            code="invalid_login",
                        )
                    user = User.objects.get(email=username)
                else:
                    user = User.objects.get(username=username)
                    if user.is_superuser:
                        raise forms.ValidationError(
                            self.error_messages["superuser_email_required"],
                            code="superuser_email_required",
                        )
            except User.DoesNotExist:
                raise forms.ValidationError(
                    self.error_messages["invalid_login"],
                    code="invalid_login",
                )

        return super().clean()
