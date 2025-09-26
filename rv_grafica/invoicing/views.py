"""Vistas del módulo de facturación."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from .forms import InvoiceFilterForm, InvoiceForm, InvoiceLineForm
from .models import Invoice


class InvoiceListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Invoice
    template_name = "invoicing/index.html"
    context_object_name = "invoices"
    permission_required = "invoicing.view_invoice"
    raise_exception = True

    def get_queryset(self):  # type: ignore[override]
        queryset = super().get_queryset().select_related("contact", "production_order")
        self.filter_form = InvoiceFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            data = self.filter_form.cleaned_data
            if data.get("document_type"):
                queryset = queryset.filter(document_type=data["document_type"])
            if data.get("contact"):
                queryset = queryset.filter(contact=data["contact"])
            if data.get("date_from"):
                queryset = queryset.filter(issue_date__gte=data["date_from"])
            if data.get("date_to"):
                queryset = queryset.filter(issue_date__lte=data["date_to"])
        return queryset

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["filter_form"] = getattr(self, "filter_form", InvoiceFilterForm())
        return context


class InvoiceCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "invoicing/form.html"
    success_url = reverse_lazy("invoicing:index")
    permission_required = "invoicing.add_invoice"
    raise_exception = True

    def form_valid(self, form):  # type: ignore[override]
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.updated_by = self.request.user
        self.object.save()
        form.save_m2m()
        messages.success(self.request, "Comprobante generado correctamente.")
        return HttpResponseRedirect(self.get_success_url())


class InvoiceUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "invoicing/form.html"
    success_url = reverse_lazy("invoicing:index")
    permission_required = "invoicing.change_invoice"
    raise_exception = True

    def form_valid(self, form):  # type: ignore[override]
        self.object = form.save(commit=False)
        self.object.updated_by = self.request.user
        self.object.save()
        form.save_m2m()
        messages.success(self.request, "Comprobante actualizado.")
        return HttpResponseRedirect(self.get_success_url())


class InvoiceDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Invoice
    template_name = "invoicing/detail.html"
    context_object_name = "invoice"
    permission_required = "invoicing.view_invoice"

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["line_form"] = InvoiceLineForm()
        return context


class InvoiceLineCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "invoicing.add_invoiceline"
    raise_exception = True

    def post(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, pk=kwargs["pk"])
        form = InvoiceLineForm(request.POST)
        if form.is_valid():
            line = form.save(commit=False)
            line.invoice = invoice
            line.save()
            messages.success(request, "Detalle agregado.")
        else:
            messages.error(request, "Revisa los datos del detalle.")
        return HttpResponseRedirect(reverse("invoicing:detail", args=[invoice.pk]))


class InvoicePostAccountingView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = "accounting.add_journalentry"
    raise_exception = True

    def post(self, request, *args, **kwargs):
        invoice = get_object_or_404(Invoice, pk=kwargs["pk"])
        invoice.post_to_accounting()
        messages.success(request, "Se generó el asiento contable asociado.")
        return HttpResponseRedirect(reverse("invoicing:detail", args=[invoice.pk]))
