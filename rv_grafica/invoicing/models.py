"""Modelos de facturación, remitos y notas de crédito."""
from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone

from rv_grafica.contacts.models import Contact
from rv_grafica.core.models import AuditableModel, TimeStampedModel


class TaxJurisdiction(models.TextChoices):
    CABA = "CABA", "Ciudad Autónoma de Buenos Aires"
    BSAS = "BSAS", "Provincia de Buenos Aires"


class Invoice(AuditableModel):
    """Documento comercial integrado con órdenes y contabilidad."""

    class DocumentType(models.TextChoices):
        SALE = "sale", "Factura de venta"
        PURCHASE = "purchase", "Factura de compra"
        SALE_CREDIT_NOTE = "sale_credit", "Nota de crédito (venta)"
        PURCHASE_CREDIT_NOTE = "purchase_credit", "Nota de crédito (compra)"
        DELIVERY_NOTE = "delivery_note", "Remito"

    number = models.CharField("número", max_length=32, unique=True)
    document_type = models.CharField("tipo", max_length=32, choices=DocumentType.choices)
    issue_date = models.DateField("fecha", default=timezone.now)
    due_date = models.DateField("vencimiento", null=True, blank=True)
    contact = models.ForeignKey(Contact, on_delete=models.PROTECT, related_name="invoices")
    production_order = models.ForeignKey(
        "rv_grafica.production.ProductionOrder",
        on_delete=models.SET_NULL,
        related_name="invoices",
        null=True,
        blank=True,
    )
    currency = models.CharField("moneda", max_length=3, default="ARS")
    vat_rate = models.DecimalField("IVA", max_digits=4, decimal_places=3, default=Decimal("0.210"))
    vat_perception = models.DecimalField("Percepción IVA", max_digits=4, decimal_places=3, default=Decimal("0.000"))
    gross_income_rate = models.DecimalField("Ingresos Brutos", max_digits=4, decimal_places=3, default=Decimal("0.000"))
    jurisdiction = models.CharField("Jurisdicción IIBB", max_length=8, choices=TaxJurisdiction.choices, blank=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    perception_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gross_income_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    observations = models.TextField("observaciones", blank=True)

    class Meta:
        ordering = ("-issue_date", "-number")
        verbose_name = "comprobante"
        verbose_name_plural = "comprobantes"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.get_document_type_display()} {self.number}"

    def save(self, *args, **kwargs):  # type: ignore[override]
        super().save(*args, **kwargs)
        self.update_totals()

    def update_totals(self) -> None:
        line_totals = self.lines.aggregate(
            net=models.Sum(models.F("quantity") * models.F("unit_price"), output_field=models.DecimalField(max_digits=12, decimal_places=2))
        )
        self.subtotal = line_totals.get("net") or Decimal("0")
        self.vat_amount = (self.subtotal * self.vat_rate).quantize(Decimal("0.01"))
        self.perception_amount = (self.subtotal * self.vat_perception).quantize(Decimal("0.01"))
        self.gross_income_amount = (self.subtotal * self.gross_income_rate).quantize(Decimal("0.01"))
        self.total = self.subtotal + self.vat_amount + self.perception_amount + self.gross_income_amount
        super().save(update_fields=["subtotal", "vat_amount", "perception_amount", "gross_income_amount", "total", "updated_at"])
        if self.production_order and self.document_type in {self.DocumentType.SALE, self.DocumentType.DELIVERY_NOTE}:
            from rv_grafica.production.models import ProductionOrder

            ProductionOrder.objects.filter(pk=self.production_order.pk).update(status=ProductionOrder.Status.COMPLETED)

    @property
    def is_sale(self) -> bool:
        return self.document_type in {self.DocumentType.SALE, self.DocumentType.SALE_CREDIT_NOTE}

    @property
    def sign(self) -> Decimal:
        return Decimal("-1") if "credit" in self.document_type else Decimal("1")

    def post_to_accounting(self) -> None:
        """Genera el asiento contable asociado al comprobante."""
        from rv_grafica.accounting.services import record_invoice_entry

        record_invoice_entry(self)


class InvoiceLine(TimeStampedModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="lines")
    description = models.CharField("concepto", max_length=255)
    quantity = models.DecimalField("cantidad", max_digits=10, decimal_places=2, default=1)
    unit_price = models.DecimalField("precio unitario", max_digits=10, decimal_places=2)
    vat_rate = models.DecimalField("IVA", max_digits=4, decimal_places=3, default=Decimal("0.210"))

    class Meta:
        verbose_name = "detalle de comprobante"
        verbose_name_plural = "detalles de comprobante"

    @property
    def subtotal(self) -> Decimal:
        return (self.quantity * self.unit_price).quantize(Decimal("0.01"))

    def save(self, *args, **kwargs):  # type: ignore[override]
        super().save(*args, **kwargs)
        self.invoice.update_totals()

    def delete(self, using=None, keep_parents=False):  # type: ignore[override]
        super().delete(using=using, keep_parents=keep_parents)
        self.invoice.update_totals()


class PaymentTerm(AuditableModel):
    """Condiciones de pago utilizadas en facturación y finanzas."""

    name = models.CharField("nombre", max_length=100, unique=True)
    days = models.PositiveIntegerField("días", default=0)
    description = models.TextField("descripción", blank=True)

    class Meta:
        verbose_name = "condición de pago"
        verbose_name_plural = "condiciones de pago"

    def __str__(self) -> str:  # pragma: no cover
        return self.name
