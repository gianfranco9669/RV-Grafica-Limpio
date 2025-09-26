from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("", views.UserListView.as_view(), name="index"),
    path("<int:pk>/editar/", views.UserUpdateView.as_view(), name="edit"),
    path("<int:pk>/desactivar/", views.deactivate_user, name="deactivate"),
]
