"""Custom user model supporting role-based permissions."""
from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Usuario del sistema con roles específicos."""

    class Roles(models.TextChoices):
        OPERATOR = "operator", "Operario"
        ADMINISTRATIVE = "administrative", "Administrativo"
        ADMIN = "admin", "Administrador"

    role = models.CharField(
        "rol",
        max_length=32,
        choices=Roles.choices,
        default=Roles.ADMINISTRATIVE,
        help_text="Determina el conjunto de permisos aplicados al usuario.",
    )

    avatar = models.ImageField("avatar", upload_to="avatars", blank=True, null=True)

    def is_operator(self) -> bool:
        return self.role == self.Roles.OPERATOR

    def is_administrative(self) -> bool:
        return self.role == self.Roles.ADMINISTRATIVE

    def is_admin(self) -> bool:
        return self.role == self.Roles.ADMIN

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
