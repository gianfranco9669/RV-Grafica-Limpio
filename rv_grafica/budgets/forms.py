"""Formularios del módulo de presupuestos."""
from __future__ import annotations

from django import forms

from rv_grafica.contacts.models import Contact

from .models import Budget, BudgetItem


class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ("title", "client", "status", "valid_until", "notes")
        widgets = {
            "valid_until": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }


class BudgetItemForm(forms.ModelForm):
    class Meta:
        model = BudgetItem
        fields = ("concept", "material", "width", "height", "quantity", "unit_price")
        widgets = {
            "width": forms.NumberInput(attrs={"step": "0.01"}),
            "height": forms.NumberInput(attrs={"step": "0.01"}),
            "unit_price": forms.NumberInput(attrs={"step": "0.01"}),
        }


class BudgetFilterForm(forms.Form):
    status = forms.ChoiceField(choices=[("", "Todos"), *Budget.Status.choices], required=False)
    client = forms.ModelChoiceField(queryset=Contact.objects.filter(is_client=True), required=False)
    valid_until = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
