"""Main URL configuration for the RV Grafica ERP system."""
from __future__ import annotations

from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="dashboard.html"), name="dashboard"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("usuarios/", include("rv_grafica.users.urls")),
    path("ordenes/", include("rv_grafica.production.urls")),
    path("presupuestos/", include("rv_grafica.budgets.urls")),
    path("facturacion/", include("rv_grafica.invoicing.urls")),
    path("terceros/", include("rv_grafica.contacts.urls")),
    path("finanzas/", include("rv_grafica.finance.urls")),
    path("contabilidad/", include("rv_grafica.accounting.urls")),
    path("stock/", include("rv_grafica.inventory.urls")),
    path("gastos/", include("rv_grafica.expenses.urls")),
    path("reportes/", include("rv_grafica.reports.urls")),
]
