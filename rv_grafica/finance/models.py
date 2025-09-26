"""Movimientos financieros de cuentas corrientes."""
from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone

from rv_grafica.contacts.models import Contact
from rv_grafica.core.models import AuditableModel


class FinanceMovement(AuditableModel):
    """Cobros y pagos asociados a clientes y proveedores."""

    class MovementType(models.TextChoices):
        COLLECTION = "collection", "Cobro"
        PAYMENT = "payment", "Pago"

    contact = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name="finance_movements")
    invoice = models.ForeignKey(
        "rv_grafica.invoicing.Invoice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="finance_movements",
    )
    movement_type = models.CharField("tipo", max_length=16, choices=MovementType.choices)
    date = models.DateField("fecha", default=timezone.now)
    amount = models.DecimalField("importe", max_digits=12, decimal_places=2)
    method = models.CharField("medio de pago", max_length=64, blank=True)
    notes = models.TextField("observaciones", blank=True)

    class Meta:
        ordering = ("-date", "-created_at")
        verbose_name = "movimiento financiero"
        verbose_name_plural = "movimientos financieros"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.get_movement_type_display()} {self.amount}"

    @property
    def signed_amount(self) -> Decimal:
        return self.amount if self.movement_type == self.MovementType.COLLECTION else -self.amount

    def post_to_accounting(self) -> None:
        from rv_grafica.accounting.services import record_finance_entry

        record_finance_entry(self)
