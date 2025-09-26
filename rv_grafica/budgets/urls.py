from django.urls import path

from . import views

app_name = "budgets"

urlpatterns = [
    path("", views.BudgetListView.as_view(), name="index"),
    path("nuevo/", views.BudgetCreateView.as_view(), name="create"),
    path("<int:pk>/", views.BudgetDetailView.as_view(), name="detail"),
    path("<int:pk>/editar/", views.BudgetUpdateView.as_view(), name="edit"),
    path("<int:pk>/items/", views.BudgetItemCreateView.as_view(), name="add_item"),
    path("<int:pk>/a-orden/", views.BudgetConvertToOrderView.as_view(), name="convert"),
]
