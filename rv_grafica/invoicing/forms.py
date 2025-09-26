"""Formularios del módulo de facturación."""
from __future__ import annotations

from django import forms
from django.db import models

from rv_grafica.contacts.models import Contact
from rv_grafica.production.models import ProductionOrder

from .models import Invoice, InvoiceLine, TaxJurisdiction


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = (
            "number",
            "document_type",
            "issue_date",
            "due_date",
            "contact",
            "production_order",
            "currency",
            "vat_rate",
            "vat_perception",
            "gross_income_rate",
            "jurisdiction",
            "observations",
        )
        widgets = {
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "observations": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contact"].queryset = Contact.objects.filter(models.Q(is_client=True) | models.Q(is_supplier=True))
        self.fields["production_order"].queryset = ProductionOrder.objects.all()
        self.fields["jurisdiction"].choices = [("", "-")] + list(TaxJurisdiction.choices)


class InvoiceLineForm(forms.ModelForm):
    class Meta:
        model = InvoiceLine
        fields = ("description", "quantity", "unit_price", "vat_rate")
        widgets = {
            "quantity": forms.NumberInput(attrs={"step": "0.01"}),
            "unit_price": forms.NumberInput(attrs={"step": "0.01"}),
            "vat_rate": forms.NumberInput(attrs={"step": "0.001"}),
        }


class InvoiceFilterForm(forms.Form):
    document_type = forms.ChoiceField(choices=[("", "Todos"), *Invoice.DocumentType.choices], required=False)
    contact = forms.ModelChoiceField(queryset=Contact.objects.all(), required=False)
    date_from = forms.DateField(label="Desde", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(label="Hasta", required=False, widget=forms.DateInput(attrs={"type": "date"}))
