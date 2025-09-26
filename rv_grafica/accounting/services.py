"""Servicios contables que conectan todos los módulos."""
from __future__ import annotations

from decimal import Decimal

from django.db import transaction

from .models import Account, JournalEntry, JournalEntryLine


def get_account(code: str, name: str) -> Account:
    account, _ = Account.objects.get_or_create(code=code, defaults={"name": name})
    return account


def record_invoice_entry(invoice) -> JournalEntry:
    """Genera un asiento a partir de una factura o nota de crédito."""
    with transaction.atomic():
        entry = JournalEntry.objects.create(
            date=invoice.issue_date,
            description=f"{invoice.get_document_type_display()} {invoice.number}",
            reference=str(invoice.pk),
        )
        sales_account = get_account("4.1", "Ventas")
        vat_account = get_account("2.1", "IVA Débito Fiscal")
        receivable_account = get_account("1.1", "Clientes")
        JournalEntryLine.objects.bulk_create(
            [
                JournalEntryLine(entry=entry, account=receivable_account, debit=invoice.total, description=invoice.contact.name),
                JournalEntryLine(entry=entry, account=sales_account, credit=invoice.subtotal, description="Ingresos"),
                JournalEntryLine(entry=entry, account=vat_account, credit=invoice.vat_amount, description="IVA"),
            ]
        )
    return entry


def record_finance_entry(movement) -> JournalEntry:
    """Asiento para cobros y pagos."""
    with transaction.atomic():
        entry = JournalEntry.objects.create(
            date=movement.date,
            description=f"{movement.get_movement_type_display()} {movement.contact.name}",
            reference=str(movement.pk),
        )
        bank_account = get_account("1.2", "Caja y Bancos")
        counterparty_account = get_account("1.1", "Clientes" if movement.movement_type == movement.MovementType.COLLECTION else "Proveedores")
        if movement.movement_type == movement.MovementType.COLLECTION:
            debit_line = JournalEntryLine(entry=entry, account=bank_account, debit=movement.amount)
            credit_line = JournalEntryLine(entry=entry, account=counterparty_account, credit=movement.amount, description=movement.contact.name)
        else:
            debit_line = JournalEntryLine(entry=entry, account=counterparty_account, debit=movement.amount, description=movement.contact.name)
            credit_line = JournalEntryLine(entry=entry, account=bank_account, credit=movement.amount)
        JournalEntryLine.objects.bulk_create([debit_line, credit_line])
    return entry


def record_expense_entry(expense) -> JournalEntry:
    """Asiento para gastos operativos."""
    with transaction.atomic():
        entry = JournalEntry.objects.create(
            date=expense.date,
            description=f"Gasto {expense.get_category_display()}",
            reference=str(expense.pk),
        )
        bank_account = get_account("1.2", "Caja y Bancos")
        expense_account = get_account("5.1", f"Gastos {expense.get_category_display()}")
        vat_credit_account = get_account("1.3", "IVA Crédito Fiscal")
        vat_amount = expense.amount * expense.vat_rate if expense.taxable else Decimal("0")
        JournalEntryLine.objects.create(entry=entry, account=expense_account, debit=expense.amount, description=expense.description)
        if vat_amount:
            JournalEntryLine.objects.create(entry=entry, account=vat_credit_account, debit=vat_amount)
        JournalEntryLine.objects.create(entry=entry, account=bank_account, credit=expense.total_with_vat(), description="Pago")
    return entry
