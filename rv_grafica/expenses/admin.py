"""Admin de gastos."""
from __future__ import annotations

from django.contrib import admin

from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("date", "category", "description", "amount", "taxable")
    list_filter = ("category", "taxable", "date")
    search_fields = ("description", "provider__name")
