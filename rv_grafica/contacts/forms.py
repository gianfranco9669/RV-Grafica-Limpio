"""Forms para clientes y proveedores."""
from __future__ import annotations

from django import forms

from .models import Contact


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = (
            "name",
            "trade_name",
            "tax_id",
            "email",
            "phone",
            "mobile",
            "address",
            "city",
            "province",
            "postal_code",
            "is_client",
            "is_supplier",
            "notes",
        )
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class ContactFilterForm(forms.Form):
    q = forms.CharField(label="Buscar", required=False)
    is_client = forms.NullBooleanField(label="Clientes", required=False)
    is_supplier = forms.NullBooleanField(label="Proveedores", required=False)
