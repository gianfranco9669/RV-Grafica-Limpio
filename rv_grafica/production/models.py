"""Modelos para gestionar las órdenes de producción."""
from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from rv_grafica.contacts.models import Contact
from rv_grafica.core.models import AuditableModel, TimeStampedModel


class ProductionOrder(AuditableModel):
    """Orden de producción integrada al resto del sistema."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pendiente"
        IN_PROGRESS = "in_progress", "En curso"
        COMPLETED = "completed", "Finalizada"

    number = models.CharField("número", max_length=20, unique=True, editable=False)
    reference = models.CharField("referencia", max_length=50, blank=True)
    description = models.TextField("descripción del trabajo")
    client = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name="orders", limit_choices_to={"is_client": True})
    status = models.CharField("estado", max_length=20, choices=Status.choices, default=Status.PENDING)
    due_date = models.DateField("fecha de entrega")
    delivery_address = models.CharField("lugar de entrega", max_length=255, blank=True)
    budget = models.ForeignKey(
        "rv_grafica.budgets.Budget",
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="assigned_orders",
        null=True,
        blank=True,
    )
    total_area_m2 = models.DecimalField("m²", max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField("importe estimado", max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = "orden de producción"
        verbose_name_plural = "órdenes de producción"
        ordering = ("-created_at",)

    def __str__(self) -> str:  # pragma: no cover
        return f"OP {self.number} - {self.client.name}"

    def save(self, *args, **kwargs):  # type: ignore[override]
        if not self.number:
            prefix = timezone.now().strftime("%y")
            last_order = ProductionOrder.objects.filter(number__startswith=prefix).order_by("number").last()
            if last_order:
                last_seq = int(last_order.number.split("-")[-1])
            else:
                last_seq = 0
            self.number = f"{prefix}-{last_seq + 1:04d}"
        if not self.description:
            self.description = "Sin descripción"
        super().save(*args, **kwargs)
        self.update_totals()

    def update_totals(self) -> None:
        """Recalcula el total en base a los ítems cargados."""
        area_expression = models.F("width") * models.F("height") * models.F("quantity")
        amount_expression = area_expression * models.F("unit_price")
        totals = self.items.aggregate(
            area=models.Sum(area_expression, output_field=models.DecimalField(max_digits=10, decimal_places=2)),
            amount=models.Sum(amount_expression, output_field=models.DecimalField(max_digits=12, decimal_places=2)),
        )
        self.total_area_m2 = totals.get("area") or Decimal("0")
        self.total_amount = totals.get("amount") or Decimal("0")
        super().save(update_fields=["total_area_m2", "total_amount", "updated_at"])

    def mark_completed(self, user=None):
        self.status = self.Status.COMPLETED
        if user:
            self.updated_by = user
        self.save(update_fields=["status", "updated_by", "updated_at"])


class OrderItem(TimeStampedModel):
    """Detalle de cada orden con cálculo por m²."""

    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name="items")
    concept = models.CharField("concepto", max_length=255)
    material = models.ForeignKey("rv_grafica.inventory.Material", on_delete=models.PROTECT, related_name="order_items")
    width = models.DecimalField("ancho (m)", max_digits=8, decimal_places=2)
    height = models.DecimalField("alto (m)", max_digits=8, decimal_places=2)
    quantity = models.PositiveIntegerField("cantidad", default=1)
    unit_price = models.DecimalField("precio unitario", max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "detalle de orden"
        verbose_name_plural = "detalles de orden"

    @property
    def area_m2(self) -> Decimal:
        return self.width * self.height * Decimal(self.quantity)

    @property
    def subtotal(self) -> Decimal:
        return self.area_m2 * self.unit_price

    def save(self, *args, **kwargs):  # type: ignore[override]
        super().save(*args, **kwargs)
        self.order.update_totals()

    def delete(self, using=None, keep_parents=False):  # type: ignore[override]
        super().delete(using=using, keep_parents=keep_parents)
        self.order.update_totals()


class MaterialUsage(TimeStampedModel):
    """Materiales asociados a la orden (reflectivo, polarizado, etc.)."""

    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name="material_usages")
    material = models.ForeignKey("rv_grafica.inventory.Material", on_delete=models.PROTECT, related_name="usages")
    quantity_used = models.DecimalField("cantidad utilizada", max_digits=10, decimal_places=2)
    unit = models.CharField("unidad", max_length=32, default="m²")

    class Meta:
        verbose_name = "uso de material"
        verbose_name_plural = "usos de material"


class OrderAttachment(TimeStampedModel):
    """Fotos y archivos de respaldo de la orden."""

    order = models.ForeignKey(ProductionOrder, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField("archivo", upload_to="order_attachments")
    description = models.CharField("descripción", max_length=255, blank=True)

    class Meta:
        verbose_name = "adjunto de orden"
        verbose_name_plural = "adjuntos de orden"
