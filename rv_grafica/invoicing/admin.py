"""Admin para facturación."""
from __future__ import annotations

from django.contrib import admin

from .models import Invoice, InvoiceLine, PaymentTerm


class InvoiceLineInline(admin.TabularInline):
    model = InvoiceLine
    extra = 0


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "document_type", "contact", "issue_date", "total")
    list_filter = ("document_type", "issue_date")
    search_fields = ("number", "contact__name")
    inlines = [InvoiceLineInline]


@admin.register(PaymentTerm)
class PaymentTermAdmin(admin.ModelAdmin):
    list_display = ("name", "days")
    search_fields = ("name",)
