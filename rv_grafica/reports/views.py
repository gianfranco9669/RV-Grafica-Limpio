"""Reportes consolidados."""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.views.generic import TemplateView

from rv_grafica.expenses.models import Expense
from rv_grafica.finance.models import FinanceMovement
from rv_grafica.invoicing.models import Invoice
from rv_grafica.production.models import ProductionOrder


class ReportsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "reports/index.html"

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        raw_orders = ProductionOrder.objects.values("status").annotate(total=Count("id"))
        context["orders_summary"] = [
            {
                "status": ProductionOrder.Status(value=row["status"]).label if row["status"] else "Sin estado",
                "total": row["total"],
            }
            for row in raw_orders
        ]
        context["invoice_totals"] = Invoice.objects.aggregate(total=Sum("total"), subtotal=Sum("subtotal"))
        context["finance_balance"] = sum(m.signed_amount for m in FinanceMovement.objects.all())
        context["expenses_total"] = Expense.objects.aggregate(total=Sum("amount"))
        return context
