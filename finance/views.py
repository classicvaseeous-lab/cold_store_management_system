from datetime import date
from calendar import monthrange
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404

from users.utils import has_any_group
from .models import BankAccount, BankTransaction
from .forms import BankAccountForm, BankTransactionForm


@login_required
@has_any_group("Admin", "Accountant", "Staff")
def account_list(request):
    accounts = BankAccount.objects.all().order_by("-is_active", "name")

    rows = []
    total_balance = Decimal("0.00")

    for a in accounts:
        credits = a.transactions.filter(tx_type="credit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
        debits  = a.transactions.filter(tx_type="debit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
        opening = a.opening_balance or Decimal("0.00")

        balance = opening + credits - debits
        total_balance += balance

        rows.append({
            "account": a,
            "credits": credits,
            "debits": debits,
            "balance": balance,
        })

    return render(request, "finance/account_list.html", {
        "rows": rows,
        "total_balance": total_balance,
    })


@login_required
@has_any_group("Admin", "Accountant")  # you can allow Staff too if you want
def account_create(request):
    if request.method == "POST":
        form = BankAccountForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Account created.")
            return redirect("finance:account_list")
        messages.error(request, "❌ Please fix the errors below.")
    else:
        form = BankAccountForm()

    return render(request, "finance/account_form.html", {
        "form": form,
        "title": "Add Account"
    })


@login_required
@has_any_group("Admin", "Accountant")  # you can allow Staff too if you want
def account_edit(request, account_id):
    account = get_object_or_404(BankAccount, id=account_id)

    if request.method == "POST":
        form = BankAccountForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Account updated.")
            return redirect("finance:account_detail", account_id=account.id)
        messages.error(request, "❌ Please fix the errors below.")
    else:
        form = BankAccountForm(instance=account)

    return render(request, "finance/account_form.html", {
        "form": form,
        "title": f"Edit: {account.name}",
        "account": account
    })


@login_required
@has_any_group("Admin", "Accountant", "Staff")
def account_detail(request, account_id):
    account = get_object_or_404(BankAccount, id=account_id)

    # Defaults: current month
    y = int(request.GET.get("y", date.today().year))
    m = int(request.GET.get("m", date.today().month))
    last_day = monthrange(y, m)[1]
    start_month = date(y, m, 1)
    end_month = date(y, m, last_day)

    # Extra filters
    date_from = request.GET.get("from", "")
    date_to = request.GET.get("to", "")
    tx_type = request.GET.get("type", "")  # credit/debit
    q = request.GET.get("q", "").strip()

    # Base queryset: month range
    tx = account.transactions.filter(date__range=(start_month, end_month))

    # Apply extra filters
    if date_from:
        tx = tx.filter(date__gte=date_from)
    if date_to:
        tx = tx.filter(date__lte=date_to)
    if tx_type in ("credit", "debit"):
        tx = tx.filter(tx_type=tx_type)
    if q:
        tx = tx.filter(
            Q(title__icontains=q) |
            Q(reference__icontains=q) |
            Q(notes__icontains=q)
        )

    tx = tx.order_by("-date", "-id")

    # Form for adding transaction
    tx_form = BankTransactionForm()

    # Monthly summary (month only, not extra filters)
    month_tx = account.transactions.filter(date__range=(start_month, end_month))
    month_credits = month_tx.filter(tx_type="credit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    month_debits  = month_tx.filter(tx_type="debit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    month_net = month_credits - month_debits

    # Totals (account overall)
    all_credits = account.transactions.filter(tx_type="credit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    all_debits  = account.transactions.filter(tx_type="debit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    opening = account.opening_balance or Decimal("0.00")
    current_balance = opening + all_credits - all_debits

    # Totals for currently displayed list (filtered tx)
    total_credits = tx.filter(tx_type="credit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    total_debits  = tx.filter(tx_type="debit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")

    return render(request, "finance/account_detail.html", {
        "account": account,
        "transactions": tx,
        "tx_form": tx_form,

        "y": y, "m": m,
        "date_from": date_from,
        "date_to": date_to,
        "tx_type": tx_type,
        "q": q,

        "current_balance": current_balance,
        "total_credits": total_credits,
        "total_debits": total_debits,

        "month_credits": month_credits,
        "month_debits": month_debits,
        "month_net": month_net,
    })


@login_required
@has_any_group("Admin", "Accountant", "Staff")
def tx_add(request, account_id):
    account = get_object_or_404(BankAccount, id=account_id)

    if request.method != "POST":
        return redirect("finance:account_detail", account_id=account.id)

    form = BankTransactionForm(request.POST)
    if form.is_valid():
        tx = form.save(commit=False)
        tx.account = account
        tx.created_by = request.user
        tx.save()
        messages.success(request, "✅ Transaction saved.")
    else:
        messages.error(request, "❌ Transaction not saved. Please check the form.")

    return redirect("finance:account_detail", account_id=account.id)


@login_required
@has_any_group("Admin", "Accountant")
def tx_delete(request, tx_id):
    tx = get_object_or_404(BankTransaction, id=tx_id)
    account_id = tx.account_id

    if request.method == "POST":
        tx.delete()
        messages.success(request, "🗑️ Transaction deleted.")

    return redirect("finance:account_detail", account_id=account_id)

# from datetime import date
# from django.db import models

# from calendar import monthrange
# from decimal import Decimal
# from django.db.models import Q, Sum
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required
# from django.db.models import Sum
# from django.shortcuts import render, redirect, get_object_or_404

# from users.utils import has_any_group
# from .models import BankAccount, BankTransaction
# from .forms import BankAccountForm, BankTransactionForm


# @login_required
# @has_any_group("Admin", "Accountant", "Staff")
# def account_list(request):
#     accounts = BankAccount.objects.all().order_by("-is_active", "name")

#     # totals per account
#     tx = (
#         BankTransaction.objects.values("account_id")
#         .annotate(
#             credits=Sum("amount", filter=models.Q(tx_type="credit")),
#             debits=Sum("amount", filter=models.Q(tx_type="debit")),
#         )
#     )

#     tx_map = {row["account_id"]: row for row in tx}

#     rows = []
#     for a in accounts:
#         row = tx_map.get(a.id, {})
#         credits = row.get("credits") or Decimal("0.00")
#         debits = row.get("debits") or Decimal("0.00")
#         balance = (a.opening_balance or Decimal("0.00")) + credits - debits

#         rows.append({
#             "account": a,
#             "credits": credits,
#             "debits": debits,
#             "balance": balance
#         })

#     # page summary (optional)
#     total_balance = sum([r["balance"] for r in rows], Decimal("0.00"))

#     return render(request, "finance/account_list.html", {
#         "rows": rows,
#         "total_balance": total_balance,
#     })
#     # remembe rto roll back to previous changes when the error keeps coming to this that is commented below
# # @login_required
# # @has_any_group("Admin", "Accountant", "Staff")
# # def account_list(request):
# #     accounts = BankAccount.objects.all()

# #     # quick summary across all active accounts (optional)
# #     active_accounts = accounts.filter(is_active=True)
# #     credits = BankTransaction.objects.filter(account__in=active_accounts, tx_type="credit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
# #     debits = BankTransaction.objects.filter(account__in=active_accounts, tx_type="debit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
# #     opening = active_accounts.aggregate(s=Sum("opening_balance"))["s"] or Decimal("0.00")
# #     total_balance = opening + credits - debits

# #     return render(request, "finance/account_list.html", {
# #         "accounts": accounts,
# #         "opening": opening,
# #         "credits": credits,
# #         "debits": debits,
# #         "total_balance": total_balance,
# #     })
 
# @login_required
# @has_any_group("Admin", "Accountant", "Staff")
# def account_detail(request, account_id):
#     account = get_object_or_404(BankAccount, id=account_id)

#     # Month filter defaults
#     y = int(request.GET.get("y", date.today().year))
#     m = int(request.GET.get("m", date.today().month))

#     last_day = monthrange(y, m)[1]
#     start_month = date(y, m, 1)
#     end_month = date(y, m, last_day)

#     # Extra filters
#     date_from = request.GET.get("from", "")
#     date_to = request.GET.get("to", "")
#     tx_type = request.GET.get("type", "")
#     q = request.GET.get("q", "").strip()

#     # Base: month range
#     tx = account.transactions.filter(date__range=(start_month, end_month))

#     # Apply additional filters
#     if date_from:
#         tx = tx.filter(date__gte=date_from)
#     if date_to:
#         tx = tx.filter(date__lte=date_to)
#     if tx_type in ("credit", "debit"):
#         tx = tx.filter(tx_type=tx_type)
#     if q:
#         tx = tx.filter(
#             Q(title__icontains=q) |
#             Q(reference__icontains=q) |
#             Q(notes__icontains=q)
#         )

#     tx = tx.order_by("-date", "-id")

#     # Summary for current filtered view
#     total_credits = tx.filter(tx_type="credit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
#     total_debits = tx.filter(tx_type="debit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")

#     # Current balance (overall, not just month) — optional:
#     all_credits = account.transactions.filter(tx_type="credit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
#     all_debits = account.transactions.filter(tx_type="debit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
#     opening = account.opening_balance or Decimal("0.00")
#     current_balance = opening + all_credits - all_debits

#     # Month net (month range, ignoring extra filters) — optional:
#     month_tx = account.transactions.filter(date__range=(start_month, end_month))
#     month_credits = month_tx.filter(tx_type="credit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
#     month_debits = month_tx.filter(tx_type="debit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
#     month_net = month_credits - month_debits

#     return render(request, "finance/account_detail.html", {
#         "account": account,
#         "transactions": tx,
#         "y": y,
#         "m": m,
#         "date_from": date_from,
#         "date_to": date_to,
#         "tx_type": tx_type,
#         "q": q,

#         "current_balance": current_balance,
#         "total_credits": total_credits,
#         "total_debits": total_debits,
#         "month_credits": month_credits,
#         "month_debits": month_debits,
#         "month_net": month_net,
#     })
# # roll back if error persists 
# # @login_required
# # @has_any_group("Admin", "Accountant", "Staff")
# # def account_detail(request, account_id):
# #     account = get_object_or_404(BankAccount, id=account_id)

# #     # filters
# #     date_from = request.GET.get("from", "")
# #     date_to = request.GET.get("to", "")
# #     tx_type = request.GET.get("type", "")  # credit / debit / ""
# #     q = request.GET.get("q", "").strip()

# #     tx = account.transactions.all()

# #     if date_from:
# #         tx = tx.filter(date__gte=date_from)
# #     if date_to:
# #         tx = tx.filter(date__lte=date_to)
# #     if tx_type in ("credit", "debit"):
# #         tx = tx.filter(tx_type=tx_type)
# #     if q:
# #         tx = tx.filter(
# #             Q(title__icontains=q) |
# #             Q(reference__icontains=q) |
# #             Q(notes__icontains=q)
# #         )

# #     tx = tx.order_by("-date", "-id")

# #     credits = tx.filter(tx_type="credit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
# #     debits = tx.filter(tx_type="debit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
# #     opening = account.opening_balance or Decimal("0.00")
# #     balance = opening + credits - debits

# #     # keep query string for pagination/buttons (optional)
# #     keep_qs = request.GET.copy()
# #     if "page" in keep_qs:
# #         keep_qs.pop("page")
# #     keep_qs = keep_qs.urlencode()

# #     return render(request, "finance/account_detail.html", {
# #         "account": account,
# #         "transactions": tx,
# #         "credits": credits,
# #         "debits": debits,
# #         "balance": balance,
# #         "date_from": date_from,
# #         "date_to": date_to,
# #         "tx_type": tx_type,
# #         "q": q,
# #         "keep_qs": keep_qs,
# #     })

# # @login_required
# # @has_any_group("Admin", "Accountant", "Staff")
# # def account_detail(request, account_id):
# #     account = get_object_or_404(BankAccount, id=account_id)

# #     # Month filter (y,m)
# #     y = int(request.GET.get("y", date.today().year))
# #     m = int(request.GET.get("m", date.today().month))
# #     last_day = monthrange(y, m)[1]
# #     start = date(y, m, 1)
# #     end = date(y, m, last_day)

# #     tx = account.transactions.filter(date__range=(start, end))

# #     month_credits = tx.filter(tx_type="credit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
# #     month_debits  = tx.filter(tx_type="debit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
# #     month_net = month_credits - month_debits

# #     # running totals (overall)
# #     total_credits = account.transactions.filter(tx_type="credit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
# #     total_debits  = account.transactions.filter(tx_type="debit").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
# #     current_balance = account.opening_balance + total_credits - total_debits

# #     tx_form = BankTransactionForm(initial={"date": date.today()})

# #     return render(request, "finance/account_detail.html", {
# #         "account": account,
# #         "transactions": tx,
# #         "tx_form": tx_form,
# #         "y": y, "m": m,
# #         "month_credits": month_credits,
# #         "month_debits": month_debits,
# #         "month_net": month_net,
# #         "current_balance": current_balance,
# #         "total_credits": total_credits,
# #         "total_debits": total_debits,
# #     })


# @login_required
# @has_any_group("Admin", "Accountant", "Staff")
# def tx_add(request, account_id):
#     account = get_object_or_404(BankAccount, id=account_id)
#     if request.method != "POST":
#         return redirect("finance:account_detail", account_id=account.id)

#     form = BankTransactionForm(request.POST)
#     if form.is_valid():
#         obj = form.save(commit=False)
#         obj.account = account
#         obj.created_by = request.user
#         obj.save()
#         messages.success(request, "✅ Transaction saved.")
#     else:
#         messages.error(request, "❌ Please check the transaction form.")

#     # keep same month view
#     y = request.GET.get("y")
#     m = request.GET.get("m")
#     qs = ""
#     if y and m:
#         qs = f"?y={y}&m={m}"
#     return redirect(f"/finance/{account.id}/{qs}".rstrip("/"))


# @login_required
# @has_any_group("Admin", "Accountant", "Staff")
# def tx_delete(request, tx_id):
#     tx = get_object_or_404(BankTransaction, id=tx_id)
#     account_id = tx.account.id

#     if request.method == "POST":
#         tx.delete()
#         messages.success(request, "🗑️ Transaction deleted.")

#     return redirect("finance:account_detail", account_id=account_id)
