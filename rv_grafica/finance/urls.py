from django.urls import path

from . import views

app_name = "finance"

urlpatterns = [
    path("", views.FinanceMovementListView.as_view(), name="index"),
    path("nuevo/", views.FinanceMovementCreateView.as_view(), name="create"),
]
