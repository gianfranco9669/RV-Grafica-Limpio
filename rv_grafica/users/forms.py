"""Forms para crear y editar usuarios."""
from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import User


class UserCreateForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "role", "avatar")


class UserUpdateForm(UserChangeForm):
    password = None

    class Meta(UserChangeForm.Meta):
        model = User
        fields = ("first_name", "last_name", "email", "role", "avatar", "is_active")


class UserFilterForm(forms.Form):
    role = forms.ChoiceField(choices=[("", "Todos"), *User.Roles.choices], required=False)
    is_active = forms.TypedChoiceField(
        label="Estado",
        choices=[("", "Todos"), ("True", "Activos"), ("False", "Inactivos")],
        coerce=str,
        required=False,
    )
