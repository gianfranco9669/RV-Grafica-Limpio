from django.urls import path

from . import views

app_name = "contacts"

urlpatterns = [
    path("", views.ContactListView.as_view(), name="index"),
    path("nuevo/", views.ContactCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", views.ContactUpdateView.as_view(), name="edit"),
]
