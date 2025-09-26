"""Modelo de gastos integrados a contabilidad."""
from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone

from rv_grafica.contacts.models import Contact
from rv_grafica.core.models import AuditableModel


class ExpenseCategory(models.TextChoices):
    FUEL = "fuel", "Nafta"
    INSURANCE = "insurance", "Seguros"
    TAX = "tax", "Impuestos"
    SERVICES = "services", "Servicios"
    OTHER = "other", "Otros"


class Expense(AuditableModel):
    """Gasto operativo con imputación contable automática."""

    date = models.DateField("fecha", default=timezone.now)
    category = models.CharField("categoría", max_length=32, choices=ExpenseCategory.choices)
    description = models.CharField("descripción", max_length=255)
    provider = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        related_name="expenses",
        null=True,
        blank=True,
        limit_choices_to={"is_supplier": True},
    )
    amount = models.DecimalField("importe", max_digits=12, decimal_places=2)
    taxable = models.BooleanField("aplica IVA", default=True)
    vat_rate = models.DecimalField("IVA", max_digits=4, decimal_places=3, default=Decimal("0.210"))
    notes = models.TextField("observaciones", blank=True)

    class Meta:
        ordering = ("-date",)
        verbose_name = "gasto"
        verbose_name_plural = "gastos"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.get_category_display()} - {self.amount}"

    def total_with_vat(self) -> Decimal:
        if not self.taxable:
            return self.amount
        return (self.amount * (Decimal("1") + self.vat_rate)).quantize(Decimal("0.01"))

    def post_to_accounting(self) -> None:
        from rv_grafica.accounting.services import record_expense_entry

        record_expense_entry(self)
