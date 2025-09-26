"""Vistas de stock."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from .forms import MaterialForm, StockAdjustmentForm
from .models import Material, StockMovement


class MaterialListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Material
    template_name = "inventory/index.html"
    context_object_name = "materials"
    permission_required = "inventory.view_material"
    raise_exception = True

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["adjustment_form"] = StockAdjustmentForm()
        return context


class MaterialCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Material
    form_class = MaterialForm
    template_name = "inventory/form.html"
    success_url = reverse_lazy("inventory:index")
    permission_required = "inventory.add_material"
    raise_exception = True

    def form_valid(self, form):  # type: ignore[override]
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.updated_by = self.request.user
        self.object.save()
        messages.success(self.request, "Material creado correctamente.")
        return HttpResponseRedirect(self.get_success_url())


class StockAdjustmentView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = StockAdjustmentForm
    template_name = "inventory/adjust.html"
    success_url = reverse_lazy("inventory:index")
    permission_required = "inventory.add_stockmovement"
    raise_exception = True

    def form_valid(self, form):  # type: ignore[override]
        movement = form.save(user=self.request.user)
        messages.success(self.request, f"Ajuste registrado: {movement.material.name} {movement.quantity}")
        return HttpResponseRedirect(self.get_success_url())
