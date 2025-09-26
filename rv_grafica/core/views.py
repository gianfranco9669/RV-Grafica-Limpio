"""Views utilitarias para páginas básicas."""
from __future__ import annotations

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def styleguide(request):
    """Renderiza componentes base para validar la interfaz."""
    return render(request, "core/styleguide.html")
