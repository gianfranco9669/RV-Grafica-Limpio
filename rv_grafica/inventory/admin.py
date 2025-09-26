"""Admin del módulo de stock."""
from __future__ import annotations

from django.contrib import admin

from .models import Material, StockMovement


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ("name", "unit", "current_stock", "minimum_stock", "unit_cost")
    search_fields = ("name", "sku", "category")


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("material", "quantity", "reason", "created_at")
    list_filter = ("reason", "created_at")
    search_fields = ("material__name", "reason", "reference")
