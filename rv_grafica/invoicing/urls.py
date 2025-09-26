from django.urls import path

from . import views

app_name = "invoicing"

urlpatterns = [
    path("", views.InvoiceListView.as_view(), name="index"),
    path("nuevo/", views.InvoiceCreateView.as_view(), name="create"),
    path("<int:pk>/", views.InvoiceDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", views.InvoiceUpdateView.as_view(), name="edit"),
    path("<int:pk>/renglones/", views.InvoiceLineCreateView.as_view(), name="add_line"),
    path("<int:pk>/contabilizar/", views.InvoicePostAccountingView.as_view(), name="post_accounting"),
]
