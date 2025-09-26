"""Vistas contables."""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Sum
from django.views.generic import ListView

from .forms import JournalFilterForm
from .models import JournalEntry, JournalEntryLine


class JournalEntryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = JournalEntry
    template_name = "accounting/index.html"
    context_object_name = "entries"
    permission_required = "accounting.view_journalentry"
    raise_exception = True

    def get_queryset(self):  # type: ignore[override]
        queryset = super().get_queryset().prefetch_related("lines__account")
        self.filter_form = JournalFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data
            if data.get("date_from"):
                queryset = queryset.filter(date__gte=data["date_from"])
            if data.get("date_to"):
                queryset = queryset.filter(date__lte=data["date_to"])
            if data.get("account"):
                queryset = queryset.filter(lines__account=data["account"]).distinct()
        return queryset

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["filter_form"] = getattr(self, "filter_form", JournalFilterForm())
        totals = JournalEntryLine.objects.aggregate(total_debit=Sum("debit"), total_credit=Sum("credit"))
        context["totals"] = totals
        return context
