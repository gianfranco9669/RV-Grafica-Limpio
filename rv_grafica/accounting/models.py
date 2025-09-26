"""Modelo contable básico."""
from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone

from rv_grafica.core.models import AuditableModel, TimeStampedModel


class Account(AuditableModel):
    """Cuenta contable."""

    code = models.CharField("código", max_length=20, unique=True)
    name = models.CharField("nombre", max_length=255)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="children", null=True, blank=True)
    is_leaf = models.BooleanField("es imputable", default=True)

    class Meta:
        ordering = ("code",)
        verbose_name = "cuenta contable"
        verbose_name_plural = "plan de cuentas"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.code} - {self.name}"


class JournalEntry(AuditableModel):
    """Asiento contable."""

    date = models.DateField("fecha", default=timezone.now)
    description = models.CharField("descripción", max_length=255)
    reference = models.CharField("referencia", max_length=128, blank=True)

    class Meta:
        ordering = ("-date", "-id")
        verbose_name = "asiento"
        verbose_name_plural = "asientos"

    def __str__(self) -> str:  # pragma: no cover
        return f"Asiento {self.pk} - {self.date}"

    @property
    def debit_total(self) -> Decimal:
        return sum(line.debit for line in self.lines.all())

    @property
    def credit_total(self) -> Decimal:
        return sum(line.credit for line in self.lines.all())


class JournalEntryLine(TimeStampedModel):
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name="lines")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="lines")
    description = models.CharField("descripción", max_length=255, blank=True)
    debit = models.DecimalField("debe", max_digits=12, decimal_places=2, default=0)
    credit = models.DecimalField("haber", max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = "renglón de asiento"
        verbose_name_plural = "renglones de asiento"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.account} {self.debit}/{self.credit}"
