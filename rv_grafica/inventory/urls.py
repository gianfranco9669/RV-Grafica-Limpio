from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.MaterialListView.as_view(), name="index"),
    path("nuevo/", views.MaterialCreateView.as_view(), name="create"),
    path("ajuste/", views.StockAdjustmentView.as_view(), name="adjust"),
]
