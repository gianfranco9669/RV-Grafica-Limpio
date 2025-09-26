"""Vistas del módulo de presupuestos."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.edit import CreateView

from .forms import BudgetFilterForm, BudgetForm, BudgetItemForm
from .models import Budget


class BudgetListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Budget
    template_name = "budgets/index.html"
    context_object_name = "budgets"
    permission_required = "budgets.view_budget"
    raise_exception = True

    def get_queryset(self):  # type: ignore[override]
        queryset = super().get_queryset().select_related("client")
        self.filter_form = BudgetFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data
            if data.get("status"):
                queryset = queryset.filter(status=data["status"])
            if data.get("client"):
                queryset = queryset.filter(client=data["client"])
            if data.get("valid_until"):
                queryset = queryset.filter(valid_until__gte=data["valid_until"])
        return queryset

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["filter_form"] = getattr(self, "filter_form", BudgetFilterForm())
        return context


class BudgetCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = "budgets/form.html"
    success_url = reverse_lazy("budgets:index")
    permission_required = "budgets.add_budget"
    raise_exception = True

    def form_valid(self, form):  # type: ignore[override]
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.updated_by = self.request.user
        self.object.save()
        form.save_m2m()
        messages.success(self.request, "Presupuesto creado correctamente.")
        return HttpResponseRedirect(self.get_success_url())


class BudgetUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Budget
    form_class = BudgetForm
    template_name = "budgets/form.html"
    success_url = reverse_lazy("budgets:index")
    permission_required = "budgets.change_budget"
    raise_exception = True

    def form_valid(self, form):  # type: ignore[override]
        self.object = form.save(commit=False)
        self.object.updated_by = self.request.user
        self.object.save()
        form.save_m2m()
        messages.success(self.request, "Presupuesto actualizado.")
        return HttpResponseRedirect(self.get_success_url())


class BudgetDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Budget
    template_name = "budgets/detail.html"
    context_object_name = "budget"
    permission_required = "budgets.view_budget"

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["item_form"] = BudgetItemForm()
        return context


class BudgetItemCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "budgets.add_budgetitem"
    raise_exception = True

    def post(self, request, *args, **kwargs):
        budget = get_object_or_404(Budget, pk=kwargs["pk"])
        form = BudgetItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.budget = budget
            item.save()
            messages.success(request, "Detalle agregado correctamente.")
        else:
            messages.error(request, "Revisa los datos cargados.")
        return HttpResponseRedirect(reverse("budgets:detail", args=[budget.pk]))


class BudgetConvertToOrderView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "production.add_productionorder"
    raise_exception = True

    def post(self, request, *args, **kwargs):
        budget = get_object_or_404(Budget, pk=kwargs["pk"])
        order = budget.convert_to_order(user=request.user)
        messages.success(request, f"Se generó la orden {order.number} vinculada al presupuesto.")
        return HttpResponseRedirect(reverse("production:detail", args=[order.pk]))
