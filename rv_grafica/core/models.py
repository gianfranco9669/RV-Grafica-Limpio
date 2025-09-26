"""Core abstract models shared across apps."""
from __future__ import annotations

from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base class that provides self-updating ``created`` and ``updated`` fields."""

    created_at = models.DateTimeField("creado", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado", auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet que implementa borrado lógico."""

    def alive(self) -> "SoftDeleteQuerySet":
        return self.filter(is_active=True)

    def deleted(self) -> "SoftDeleteQuerySet":
        return self.filter(is_active=False)


class SoftDeleteModel(TimeStampedModel):
    """Abstract base class with a boolean flag for logical deletes."""

    is_active = models.BooleanField("activo", default=True)

    objects = SoftDeleteQuerySet.as_manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):  # type: ignore[override]
        self.is_active = False
        self.save(update_fields=["is_active"])


class AuditableModel(SoftDeleteModel):
    """Adds audit information about the user that created or modified a record."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_%(class)ss",
        null=True,
        blank=True,
        verbose_name="creado por",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="updated_%(class)ss",
        null=True,
        blank=True,
        verbose_name="actualizado por",
    )

    class Meta:
        abstract = True
