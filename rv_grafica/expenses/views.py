"""Vistas de gastos."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from .forms import ExpenseFilterForm, ExpenseForm
from .models import Expense


class ExpenseListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Expense
    template_name = "expenses/index.html"
    context_object_name = "expenses"
    permission_required = "expenses.view_expense"
    raise_exception = True

    def get_queryset(self):  # type: ignore[override]
        queryset = super().get_queryset().select_related("provider")
        self.filter_form = ExpenseFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data
            if data.get("category"):
                queryset = queryset.filter(category=data["category"])
            if data.get("provider"):
                queryset = queryset.filter(provider__name__icontains=data["provider"])
            if data.get("date_from"):
                queryset = queryset.filter(date__gte=data["date_from"])
            if data.get("date_to"):
                queryset = queryset.filter(date__lte=data["date_to"])
        return queryset

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["filter_form"] = getattr(self, "filter_form", ExpenseFilterForm())
        context["form"] = ExpenseForm()
        return context


class ExpenseCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = "expenses/form.html"
    success_url = reverse_lazy("expenses:index")
    permission_required = "expenses.add_expense"
    raise_exception = True

    def form_valid(self, form):  # type: ignore[override]
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.updated_by = self.request.user
        self.object.save()
        self.object.post_to_accounting()
        messages.success(self.request, "Gasto registrado y contabilizado.")
        return HttpResponseRedirect(self.get_success_url())
