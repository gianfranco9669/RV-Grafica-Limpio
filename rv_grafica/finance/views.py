"""Vistas de finanzas."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from .forms import FinanceFilterForm, FinanceMovementForm
from .models import FinanceMovement


class FinanceMovementListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = FinanceMovement
    template_name = "finance/index.html"
    context_object_name = "movements"
    permission_required = "finance.view_financemovement"
    raise_exception = True

    def get_queryset(self):  # type: ignore[override]
        queryset = super().get_queryset().select_related("contact", "invoice")
        self.filter_form = FinanceFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data
            if data.get("movement_type"):
                queryset = queryset.filter(movement_type=data["movement_type"])
            if data.get("contact"):
                queryset = queryset.filter(contact__name__icontains=data["contact"])
            if data.get("date_from"):
                queryset = queryset.filter(date__gte=data["date_from"])
            if data.get("date_to"):
                queryset = queryset.filter(date__lte=data["date_to"])
        return queryset

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["filter_form"] = getattr(self, "filter_form", FinanceFilterForm())
        context["form"] = FinanceMovementForm()
        context["balance"] = sum(m.signed_amount for m in context["movements"])
        return context


class FinanceMovementCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = FinanceMovement
    form_class = FinanceMovementForm
    template_name = "finance/form.html"
    success_url = reverse_lazy("finance:index")
    permission_required = "finance.add_financemovement"
    raise_exception = True

    def form_valid(self, form):  # type: ignore[override]
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.updated_by = self.request.user
        self.object.save()
        self.object.post_to_accounting()
        messages.success(self.request, "Movimiento registrado en cuenta corriente.")
        return HttpResponseRedirect(self.get_success_url())
