"""Formularios de finanzas."""
from __future__ import annotations

from django import forms
from django.db import models

from rv_grafica.contacts.models import Contact

from .models import FinanceMovement


class FinanceMovementForm(forms.ModelForm):
    class Meta:
        model = FinanceMovement
        fields = ("contact", "invoice", "movement_type", "date", "amount", "method", "notes")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contact"].queryset = Contact.objects.filter(models.Q(is_client=True) | models.Q(is_supplier=True))


class FinanceFilterForm(forms.Form):
    contact = forms.CharField(required=False)
    movement_type = forms.ChoiceField(choices=[("", "Todos"), *FinanceMovement.MovementType.choices], required=False)
    date_from = forms.DateField(label="Desde", required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(label="Hasta", required=False, widget=forms.DateInput(attrs={"type": "date"}))
