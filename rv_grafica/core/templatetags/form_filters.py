"""Filtros de template para mejorar la presentación de formularios."""
from __future__ import annotations

from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(value, css_class):
    if hasattr(value, "as_widget"):
        attrs = value.field.widget.attrs
        existing_classes = attrs.get("class", "")
        attrs["class"] = f"{existing_classes} {css_class}".strip()
        return value
    return value
