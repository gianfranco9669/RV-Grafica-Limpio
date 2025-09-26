"""Admin del módulo contable."""
from __future__ import annotations

from django.contrib import admin

from .models import Account, JournalEntry, JournalEntryLine


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 0


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "parent", "is_leaf")
    list_filter = ("is_leaf",)
    search_fields = ("code", "name")


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "description")
    date_hierarchy = "date"
    inlines = [JournalEntryLineInline]
