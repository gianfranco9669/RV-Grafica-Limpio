"""Formularios de gastos."""
from __future__ import annotations

from django import forms

from .models import Expense, ExpenseCategory


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ("date", "category", "description", "provider", "amount", "taxable", "vat_rate", "notes")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class ExpenseFilterForm(forms.Form):
    category = forms.ChoiceField(choices=[("", "Todas"), *ExpenseCategory.choices], required=False)
    provider = forms.CharField(required=False)
    date_from = forms.DateField(label="Desde", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(label="Hasta", required=False, widget=forms.DateInput(attrs={"type": "date"}))
