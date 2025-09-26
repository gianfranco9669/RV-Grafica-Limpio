"""Vistas del módulo de terceros."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import ContactFilterForm, ContactForm
from .models import Contact


class ContactListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Contact
    template_name = "contacts/index.html"
    context_object_name = "contacts"
    permission_required = "contacts.view_contact"
    raise_exception = True

    def get_queryset(self):  # type: ignore[override]
        queryset = super().get_queryset().alive().select_related("created_by")
        self.filter_form = ContactFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            q = self.filter_form.cleaned_data.get("q")
            if q:
                queryset = queryset.filter(name__icontains=q)
            is_client = self.filter_form.cleaned_data.get("is_client")
            if is_client is True:
                queryset = queryset.filter(is_client=True)
            elif is_client is False:
                queryset = queryset.filter(is_client=False)
            is_supplier = self.filter_form.cleaned_data.get("is_supplier")
            if is_supplier is True:
                queryset = queryset.filter(is_supplier=True)
            elif is_supplier is False:
                queryset = queryset.filter(is_supplier=False)
        return queryset

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["filter_form"] = getattr(self, "filter_form", ContactFilterForm())
        return context


class ContactCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Contact
    form_class = ContactForm
    template_name = "contacts/form.html"
    success_url = reverse_lazy("contacts:index")
    permission_required = "contacts.add_contact"
    raise_exception = True

    def form_valid(self, form):  # type: ignore[override]
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.updated_by = self.request.user
        self.object.save()
        form.save_m2m()
        messages.success(self.request, "Contacto creado correctamente.")
        return HttpResponseRedirect(self.get_success_url())


class ContactUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Contact
    form_class = ContactForm
    template_name = "contacts/form.html"
    success_url = reverse_lazy("contacts:index")
    permission_required = "contacts.change_contact"
    raise_exception = True

    def form_valid(self, form):  # type: ignore[override]
        self.object = form.save(commit=False)
        self.object.updated_by = self.request.user
        self.object.save()
        form.save_m2m()
        messages.success(self.request, "Contacto actualizado.")
        return HttpResponseRedirect(self.get_success_url())
