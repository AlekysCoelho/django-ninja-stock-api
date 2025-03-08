import re

from django import forms
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    UserChangeForm,
    UserCreationForm,
)
from django.contrib.messages import constants
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class UserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + ("bio",)


class UserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + ("bio",)


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
            "Please enter a correct %(username)s and password.Please not that both fields are case sensitive."
        ),
        "superuser_email_required": _("Super user must log in using email."),
        "inactive": _("This accounts is inactive."),
    }

    def clean(self):
        username = self.cleaned_data.get("username").strip()
        password = self.cleaned_data.get("password").strip()

        if username and password:
            if len(username) > 254 or len(password) > 50:
                messages.add_message(
                    self.request,
                    constants.ERROR,
                    _(self.error_messages["invalid_login"]),
                )

            try:
                if "@" in username:
                    if not re.match(
                        r"^(?=.{3,254}$)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                        username,
                    ):
                        messages.add_message(
                            self.request,
                            constants.ERROR,
                            _(self.error_messages["invalid_login"]),
                        )
                    user = User.objects.get(email=username)
                else:
                    user = User.objects.get(username=username)
                    if user.is_superuser:
                        messages.add_message(
                            self.request,
                            constants.WARNING,
                            _(self.error_messages["superuser_email_requered"]),
                        )
            except User.DoesNotExist:
                messages.add_message(
                    self.request,
                    constants.ERROR,
                    _(self.error_messages["invalid_login"]),
                )

        return self.cleaned_data
