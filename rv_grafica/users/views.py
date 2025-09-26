"""Views para la administración de usuarios."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, UpdateView

from .forms import UserFilterForm, UserUpdateForm
from .models import User


class UserListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = User
    template_name = "users/index.html"
    context_object_name = "users"
    permission_required = "users.view_user"
    raise_exception = True

    def get_queryset(self):  # type: ignore[override]
        queryset = super().get_queryset().order_by("first_name", "last_name")
        self.filter_form = UserFilterForm(self.request.GET or None)
        if self.filter_form.is_valid():
            role = self.filter_form.cleaned_data.get("role")
            if role:
                queryset = queryset.filter(role=role)
            is_active = self.filter_form.cleaned_data.get("is_active")
            if is_active == "True":
                queryset = queryset.filter(is_active=True)
            elif is_active == "False":
                queryset = queryset.filter(is_active=False)
        return queryset

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        context["filter_form"] = getattr(self, "filter_form", UserFilterForm())
        return context


class UserUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "users/form.html"
    success_url = reverse_lazy("users:index")
    permission_required = "users.change_user"
    raise_exception = True

    def form_valid(self, form):  # type: ignore[override]
        messages.success(self.request, "Usuario actualizado correctamente.")
        return super().form_valid(form)


@login_required
@permission_required("users.change_user", raise_exception=True)
def deactivate_user(request, pk):
    user = User.objects.get(pk=pk)
    user.is_active = False
    user.save(update_fields=["is_active"])
    messages.info(request, f"Se desactivó al usuario {user}.")
    return redirect("users:index")
