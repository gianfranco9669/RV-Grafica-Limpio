"""Vistas para gestionar las órdenes de producción."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.edit import CreateView

from .forms import MaterialUsageForm, OrderItemForm, ProductionOrderFilterForm, ProductionOrderForm
from .models import MaterialUsage, OrderItem, ProductionOrder


class OrderListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = ProductionOrder
    template_name = "production/index.html"
    context_object_name = "orders"
    permission_required = "production.view_productionorder"
    raise_exception = True

    def get_queryset(self):  # type: ignore[override]
        queryset = super().get_queryset().select_related("client", "assigned_to")
        self.filter_form = ProductionOrderFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data
            if data.get("status"):
                queryset = queryset.filter(status=data["status"])
            if data.get("client"):
                queryset = queryset.filter(client=data["client"])
            if data.get("due_date_from"):
                queryset = queryset.filter(due_date__gte=data["due_date_from"])
            if data.get("due_date_to"):
                queryset = queryset.filter(due_date__lte=data["due_date_to"])
        return queryset

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["filter_form"] = getattr(self, "filter_form", ProductionOrderFilterForm())
        return context


class OrderCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = ProductionOrder
    form_class = ProductionOrderForm
    template_name = "production/form.html"
    success_url = reverse_lazy("production:index")
    permission_required = "production.add_productionorder"
    raise_exception = True

    def form_valid(self, form):  # type: ignore[override]
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.updated_by = self.request.user
        self.object.save()
        form.save_m2m()
        messages.success(self.request, "Orden creada correctamente.")
        return HttpResponseRedirect(self.get_success_url())


class OrderUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = ProductionOrder
    form_class = ProductionOrderForm
    template_name = "production/form.html"
    success_url = reverse_lazy("production:index")
    permission_required = "production.change_productionorder"
    raise_exception = True

    def form_valid(self, form):  # type: ignore[override]
        self.object = form.save(commit=False)
        self.object.updated_by = self.request.user
        self.object.save()
        form.save_m2m()
        messages.success(self.request, "Orden actualizada.")
        return HttpResponseRedirect(self.get_success_url())


class OrderDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = ProductionOrder
    template_name = "production/detail.html"
    context_object_name = "order"
    permission_required = "production.view_productionorder"

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["item_form"] = OrderItemForm()
        context["material_form"] = MaterialUsageForm()
        return context


class OrderItemCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "production.add_orderitem"
    raise_exception = True

    def post(self, request, *args, **kwargs):
        order = get_object_or_404(ProductionOrder, pk=kwargs["pk"])
        form = OrderItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.order = order
            item.save()
            messages.success(request, "Detalle agregado correctamente.")
        else:
            messages.error(request, "Revisa los datos del detalle.")
        return HttpResponseRedirect(reverse("production:detail", args=[order.pk]))


class MaterialUsageCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "production.add_materialusage"
    raise_exception = True

    def post(self, request, *args, **kwargs):
        order = get_object_or_404(ProductionOrder, pk=kwargs["pk"])
        form = MaterialUsageForm(request.POST)
        if form.is_valid():
            usage = form.save(commit=False)
            usage.order = order
            usage.save()
            messages.success(request, "Material registrado.")
        else:
            messages.error(request, "Revisa los datos del material.")
        return HttpResponseRedirect(reverse("production:detail", args=[order.pk]))


class OrderChangeStatusView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "production.change_productionorder"

    def post(self, request, *args, **kwargs):
        order = get_object_or_404(ProductionOrder, pk=kwargs["pk"])
        new_status = request.POST.get("status")
        if new_status in dict(ProductionOrder.Status.choices):
            order.status = new_status
            order.updated_by = request.user
            order.save(update_fields=["status", "updated_by", "updated_at"])
            messages.success(request, "Estado actualizado.")
        else:
            messages.error(request, "Estado inválido.")
        return HttpResponseRedirect(reverse("production:detail", args=[order.pk]))
