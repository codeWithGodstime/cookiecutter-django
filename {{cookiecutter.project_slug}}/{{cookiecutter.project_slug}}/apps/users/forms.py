from django.contrib.auth import forms as admin_forms
{%- if cookiecutter.username_type == "email" %}
from django.forms import EmailField
{%- endif %}
from django.utils.translation import gettext_lazy as _

from .models import User


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):  # type: ignore[name-defined]
        model = User
        {%- if cookiecutter.username_type == "email" %}
        field_classes = {"email": EmailField}
        {%- endif %}


class UserAdminCreationForm(admin_forms.AdminUserCreationForm):
    """
    Form for User Creation in the Admin Area.
    """

    class Meta(admin_forms.UserCreationForm.Meta):  # type: ignore[name-defined]
        model = User
        {%- if cookiecutter.username_type == "email" %}
        fields = ("email",)
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }
        {%- else %}
        error_messages = {
            "username": {"unique": _("This username has already been taken.")},
        }
        {%- endif %}
