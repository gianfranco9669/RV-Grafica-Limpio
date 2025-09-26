"""Formularios para las órdenes de producción."""
from __future__ import annotations

from django import forms

from rv_grafica.contacts.models import Contact

from .models import MaterialUsage, OrderItem, ProductionOrder


class ProductionOrderForm(forms.ModelForm):
    class Meta:
        model = ProductionOrder
        fields = (
            "reference",
            "description",
            "client",
            "status",
            "due_date",
            "delivery_address",
            "budget",
            "assigned_to",
        )
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ("concept", "material", "width", "height", "quantity", "unit_price")
        widgets = {
            "width": forms.NumberInput(attrs={"step": "0.01"}),
            "height": forms.NumberInput(attrs={"step": "0.01"}),
            "unit_price": forms.NumberInput(attrs={"step": "0.01"}),
        }


class MaterialUsageForm(forms.ModelForm):
    class Meta:
        model = MaterialUsage
        fields = ("material", "quantity_used", "unit")
        widgets = {
            "quantity_used": forms.NumberInput(attrs={"step": "0.01"}),
        }


class ProductionOrderFilterForm(forms.Form):
    status = forms.ChoiceField(choices=[("", "Todos los estados"), *ProductionOrder.Status.choices], required=False)
    due_date_from = forms.DateField(label="Desde", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    due_date_to = forms.DateField(label="Hasta", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    client = forms.ModelChoiceField(label="Cliente", queryset=Contact.objects.filter(is_client=True), required=False)
