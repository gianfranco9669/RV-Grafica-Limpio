"""Admin de finanzas."""
from __future__ import annotations

from django.contrib import admin

from .models import FinanceMovement


@admin.register(FinanceMovement)
class FinanceMovementAdmin(admin.ModelAdmin):
    list_display = ("date", "movement_type", "contact", "amount")
    list_filter = ("movement_type", "date")
    search_fields = ("contact__name", "invoice__number", "method")
