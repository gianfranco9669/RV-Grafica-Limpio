"""Admin para presupuestos."""
from __future__ import annotations

from django.contrib import admin

from .models import Budget, BudgetItem


class BudgetItemInline(admin.TabularInline):
    model = BudgetItem
    extra = 0


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ("number", "client", "status", "valid_until", "total_amount")
    list_filter = ("status", "valid_until")
    search_fields = ("number", "client__name", "title")
    inlines = [BudgetItemInline]
