"""Admin para contactos."""
from __future__ import annotations

from django.contrib import admin

from .models import Contact, ContactAccount


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "tax_id", "email", "is_client", "is_supplier", "is_active")
    list_filter = ("is_client", "is_supplier", "is_active")
    search_fields = ("name", "tax_id", "email")
    autocomplete_fields = ("created_by", "updated_by")


@admin.register(ContactAccount)
class ContactAccountAdmin(admin.ModelAdmin):
    list_display = ("contact", "credit_limit", "payment_terms")
    search_fields = ("contact__name", "contact__tax_id")
