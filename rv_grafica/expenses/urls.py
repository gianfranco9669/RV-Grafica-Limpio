from django.urls import path

from . import views

app_name = "expenses"

urlpatterns = [
    path("", views.ExpenseListView.as_view(), name="index"),
    path("nuevo/", views.ExpenseCreateView.as_view(), name="create"),
]
