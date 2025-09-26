"""Modelos para gestionar clientes y proveedores."""
from __future__ import annotations

from django.db import models

from rv_grafica.core.models import AuditableModel


class Contact(AuditableModel):
    """Contacto genérico que puede actuar como cliente o proveedor."""

    name = models.CharField("razón social", max_length=255)
    trade_name = models.CharField("nombre fantasía", max_length=255, blank=True)
    tax_id = models.CharField("CUIT/CUIL", max_length=20, unique=True)
    email = models.EmailField("correo", blank=True)
    phone = models.CharField("teléfono", max_length=50, blank=True)
    mobile = models.CharField("celular", max_length=50, blank=True)
    address = models.CharField("domicilio", max_length=255, blank=True)
    city = models.CharField("localidad", max_length=128, blank=True)
    province = models.CharField("provincia", max_length=128, blank=True)
    postal_code = models.CharField("código postal", max_length=12, blank=True)
    is_client = models.BooleanField("es cliente", default=False)
    is_supplier = models.BooleanField("es proveedor", default=False)
    notes = models.TextField("observaciones", blank=True)

    class Meta:
        verbose_name = "contacto"
        verbose_name_plural = "contactos"
        ordering = ("name",)

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class ContactAccount(AuditableModel):
    """Cuenta corriente asociada a un contacto."""

    contact = models.OneToOneField(Contact, on_delete=models.CASCADE, related_name="account")
    credit_limit = models.DecimalField("límite de crédito", max_digits=12, decimal_places=2, default=0)
    payment_terms = models.CharField("condiciones", max_length=255, blank=True)

    class Meta:
        verbose_name = "cuenta de contacto"
        verbose_name_plural = "cuentas de contacto"

    def __str__(self) -> str:  # pragma: no cover
        return f"Cuenta de {self.contact.name}"
