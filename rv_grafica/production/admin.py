"""Admin para órdenes de producción."""
from __future__ import annotations

from django.contrib import admin

from .models import MaterialUsage, OrderAttachment, OrderItem, ProductionOrder


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


class MaterialUsageInline(admin.TabularInline):
    model = MaterialUsage
    extra = 0


@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ("number", "client", "status", "due_date", "total_amount")
    list_filter = ("status", "due_date")
    search_fields = ("number", "client__name", "description")
    date_hierarchy = "due_date"
    inlines = [OrderItemInline, MaterialUsageInline]


@admin.register(OrderAttachment)
class OrderAttachmentAdmin(admin.ModelAdmin):
    list_display = ("order", "description", "created_at")
    search_fields = ("order__number", "description")
