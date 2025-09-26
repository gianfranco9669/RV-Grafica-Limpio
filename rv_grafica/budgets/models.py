"""Modelos de presupuestos."""
from __future__ import annotations

from decimal import Decimal

from django.db import models
from django.utils import timezone

from rv_grafica.contacts.models import Contact
from rv_grafica.core.models import AuditableModel, TimeStampedModel


class Budget(AuditableModel):
    """Cotización con cálculo por metro cuadrado."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Borrador"
        SENT = "sent", "Enviado"
        APPROVED = "approved", "Aprobado"
        REJECTED = "rejected", "Rechazado"

    number = models.CharField("número", max_length=20, unique=True, editable=False)
    title = models.CharField("título", max_length=255)
    client = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name="budgets", limit_choices_to={"is_client": True})
    status = models.CharField("estado", max_length=20, choices=Status.choices, default=Status.DRAFT)
    valid_until = models.DateField("vigencia", default=timezone.now)
    notes = models.TextField("observaciones", blank=True)
    total_area_m2 = models.DecimalField("m²", max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField("importe", max_digits=12, decimal_places=2, default=0)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "presupuesto"
        verbose_name_plural = "presupuestos"

    def __str__(self) -> str:  # pragma: no cover
        return f"Presupuesto {self.number} - {self.client.name}"

    def save(self, *args, **kwargs):  # type: ignore[override]
        if not self.number:
            prefix = timezone.now().strftime("P%y")
            last_budget = Budget.objects.filter(number__startswith=prefix).order_by("number").last()
            sequence = int(last_budget.number.split("-")[-1]) if last_budget else 0
            self.number = f"{prefix}-{sequence + 1:04d}"
        super().save(*args, **kwargs)
        self.update_totals()

    def update_totals(self) -> None:
        area_expression = models.F("width") * models.F("height") * models.F("quantity")
        amount_expression = area_expression * models.F("unit_price")
        totals = self.items.aggregate(
            area=models.Sum(area_expression, output_field=models.DecimalField(max_digits=10, decimal_places=2)),
            amount=models.Sum(amount_expression, output_field=models.DecimalField(max_digits=12, decimal_places=2)),
        )
        self.total_area_m2 = totals.get("area") or Decimal("0")
        self.total_amount = totals.get("amount") or Decimal("0")
        super().save(update_fields=["total_area_m2", "total_amount", "updated_at"])

    def convert_to_order(self, user=None):
        from rv_grafica.production.models import ProductionOrder

        order = ProductionOrder.objects.create(
            description=self.title,
            client=self.client,
            status=ProductionOrder.Status.PENDING,
            due_date=self.valid_until,
            budget=self,
            created_by=user,
            updated_by=user,
        )
        for item in self.items.all():
            order.items.create(
                concept=item.concept,
                material=item.material,
                width=item.width,
                height=item.height,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
        order.update_totals()
        self.status = self.Status.APPROVED
        self.save(update_fields=["status", "updated_at"])
        return order


class BudgetItem(TimeStampedModel):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="items")
    concept = models.CharField("concepto", max_length=255)
    material = models.ForeignKey("rv_grafica.inventory.Material", on_delete=models.PROTECT, related_name="budget_items")
    width = models.DecimalField("ancho (m)", max_digits=8, decimal_places=2)
    height = models.DecimalField("alto (m)", max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField("cantidad", default=1)
    unit_price = models.DecimalField("precio unitario", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "detalle de presupuesto"
        verbose_name_plural = "detalles de presupuesto"

    @property
    def area_m2(self) -> Decimal:
        return self.width * self.height * Decimal(self.quantity)

    @property
    def subtotal(self) -> Decimal:
        return self.area_m2 * self.unit_price

    def save(self, *args, **kwargs):  # type: ignore[override]
        super().save(*args, **kwargs)
        self.budget.update_totals()

    def delete(self, using=None, keep_parents=False):  # type: ignore[override]
        super().delete(using=using, keep_parents=keep_parents)
        self.budget.update_totals()
