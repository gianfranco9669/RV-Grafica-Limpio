from django.urls import path

from . import views

app_name = "production"

urlpatterns = [
    path("", views.OrderListView.as_view(), name="index"),
    path("nueva/", views.OrderCreateView.as_view(), name="create"),
    path("<int:pk>/", views.OrderDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", views.OrderUpdateView.as_view(), name="edit"),
    path("<int:pk>/estado/", views.OrderChangeStatusView.as_view(), name="change_status"),
    path("<int:pk>/items/", views.OrderItemCreateView.as_view(), name="add_item"),
    path("<int:pk>/materiales/", views.MaterialUsageCreateView.as_view(), name="add_material"),
]
