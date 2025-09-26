"""Modelos para gestionar materiales e inventario."""
from __future__ import annotations

from decimal import Decimal

from django.db import models

from rv_grafica.core.models import AuditableModel


class Material(AuditableModel):
    """Insumos como vinilos, lonas, polarizados, etc."""

    name = models.CharField("nombre", max_length=255, unique=True)
    sku = models.CharField("código", max_length=64, blank=True)
    category = models.CharField("categoría", max_length=128, blank=True)
    unit = models.CharField("unidad", max_length=32, default="m²")
    current_stock = models.DecimalField("stock actual", max_digits=12, decimal_places=2, default=0)
    minimum_stock = models.DecimalField("stock mínimo", max_digits=12, decimal_places=2, default=0)
    unit_cost = models.DecimalField("costo unitario", max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ("name",)
        verbose_name = "material"
        verbose_name_plural = "materiales"

    def __str__(self) -> str:  # pragma: no cover
        return self.name

    def adjust_stock(self, quantity: Decimal, reason: str, reference: str | None = None):
        movement = StockMovement.objects.create(
            material=self,
            quantity=quantity,
            reason=reason,
            reference=reference or "ajuste manual",
            created_by=self.updated_by,
            updated_by=self.updated_by,
        )
        self.current_stock = self.current_stock + quantity
        self.save(update_fields=["current_stock", "updated_at"])
        return movement


class StockMovement(AuditableModel):
    """Movimientos de inventario integrados con órdenes y facturación."""

    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name="movements")
    quantity = models.DecimalField("cantidad", max_digits=12, decimal_places=2)
    reason = models.CharField("motivo", max_length=255)
    reference = models.CharField("referencia", max_length=128, blank=True)
    order = models.ForeignKey(
        "rv_grafica.production.ProductionOrder",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )
    invoice = models.ForeignKey(
        "rv_grafica.invoicing.Invoice",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_movements",
    )

    class Meta:
        verbose_name = "movimiento de stock"
        verbose_name_plural = "movimientos de stock"
        ordering = ("-created_at",)

    def save(self, *args, **kwargs):  # type: ignore[override]
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.material.current_stock = self.material.current_stock + self.quantity
            self.material.save(update_fields=["current_stock", "updated_at"])
