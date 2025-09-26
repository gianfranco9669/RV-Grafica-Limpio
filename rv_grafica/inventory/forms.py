"""Formularios de stock."""
from __future__ import annotations

from decimal import Decimal

from django import forms

from .models import Material, StockMovement


class MaterialForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ("name", "sku", "category", "unit", "minimum_stock", "unit_cost")


class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ("material", "quantity", "reason", "reference", "order", "invoice")
        widgets = {
            "quantity": forms.NumberInput(attrs={"step": "0.01"}),
        }


class StockAdjustmentForm(forms.Form):
    material = forms.ModelChoiceField(queryset=Material.objects.all())
    quantity = forms.DecimalField(max_digits=12, decimal_places=2)
    reason = forms.CharField(max_length=255)
    reference = forms.CharField(max_length=128, required=False)

    def save(self, user=None) -> StockMovement:
        material: Material = self.cleaned_data["material"]
        material.updated_by = user
        return material.adjust_stock(
            quantity=Decimal(self.cleaned_data["quantity"]),
            reason=self.cleaned_data["reason"],
            reference=self.cleaned_data.get("reference"),
        )
