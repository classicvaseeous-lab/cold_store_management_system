from datetime import date
from calendar import monthrange
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from users.utils import has_any_group
from .models import BankAccount, BankTransaction
from .forms import BankAccountForm, BankTransactionForm


@login_required
@has_any_group("Admin", "Accountant", "Staff")
def account_list(request):
    accounts = BankAccount.objects.all()

    # quick summary across all active accounts (optional)
    active_accounts = accounts.filter(is_active=True)
    credits = BankTransaction.objects.filter(account__in=active_accounts, tx_type="credit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    debits = BankTransaction.objects.filter(account__in=active_accounts, tx_type="debit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    opening = active_accounts.aggregate(s=Sum("opening_balance"))["s"] or Decimal("0.00")
    total_balance = opening + credits - debits

    return render(request, "finance/account_list.html", {
        "accounts": accounts,
        "opening": opening,
        "credits": credits,
        "debits": debits,
        "total_balance": total_balance,
    })


@login_required
@has_any_group("Admin", "Accountant", "Staff")
def account_detail(request, account_id):
    account = get_object_or_404(BankAccount, id=account_id)

    # Month filter (y,m)
    y = int(request.GET.get("y", date.today().year))
    m = int(request.GET.get("m", date.today().month))
    last_day = monthrange(y, m)[1]
    start = date(y, m, 1)
    end = date(y, m, last_day)

    tx = account.transactions.filter(date__range=(start, end))

    month_credits = tx.filter(tx_type="credit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    month_debits  = tx.filter(tx_type="debit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    month_net = month_credits - month_debits

    # running totals (overall)
    total_credits = account.transactions.filter(tx_type="credit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    total_debits  = account.transactions.filter(tx_type="debit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    current_balance = account.opening_balance + total_credits - total_debits

    tx_form = BankTransactionForm(initial={"date": date.today()})

    return render(request, "finance/account_detail.html", {
        "account": account,
        "transactions": tx,
        "tx_form": tx_form,
        "y": y, "m": m,
        "month_credits": month_credits,
        "month_debits": month_debits,
        "month_net": month_net,
        "current_balance": current_balance,
        "total_credits": total_credits,
        "total_debits": total_debits,
    })


@login_required
@has_any_group("Admin", "Accountant", "Staff")
def tx_add(request, account_id):
    account = get_object_or_404(BankAccount, id=account_id)
    if request.method != "POST":
        return redirect("finance:account_detail", account_id=account.id)

    form = BankTransactionForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.account = account
        obj.created_by = request.user
        obj.save()
        messages.success(request, "✅ Transaction saved.")
    else:
        messages.error(request, "❌ Please check the transaction form.")

    # keep same month view
    y = request.GET.get("y")
    m = request.GET.get("m")
    qs = ""
    if y and m:
        qs = f"?y={y}&m={m}"
    return redirect(f"/finance/{account.id}/{qs}".rstrip("/"))


@login_required
@has_any_group("Admin", "Accountant", "Staff")
def tx_delete(request, tx_id):
    tx = get_object_or_404(BankTransaction, id=tx_id)
    account_id = tx.account.id

    if request.method == "POST":
        tx.delete()
        messages.success(request, "🗑️ Transaction deleted.")

    return redirect("finance:account_detail", account_id=account_id)
