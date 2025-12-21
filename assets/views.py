from datetime import date
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from users.utils import has_any_group
from .models import Vehicle, VehicleTransaction
from .forms import VehicleTransactionForm, VehicleForm


@login_required
@has_any_group("Admin", "Accountant", "Staff")
def add_vehicle(request):
    if request.method == "POST":
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("assets:vehicle_list")
    else:
        form = VehicleForm()

    return render(request, "assets/vehicle_form.html", {"form": form})


@login_required
@has_any_group("Admin", "Accountant", "Staff")
def vehicle_list(request):
    vehicles = Vehicle.objects.all().order_by("-id")
    return render(request, "assets/vehicle_list.html", {"vehicles": vehicles})


@login_required
@has_any_group("Admin", "Accountant", "Staff")
def vehicle_detail(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    tx = vehicle.transactions.all()

    # ✅ Support the from/to filter used in your template
    date_from = request.GET.get("from") or ""
    date_to = request.GET.get("to") or ""

    if date_from:
        tx = tx.filter(date__gte=date_from)
    if date_to:
        tx = tx.filter(date__lte=date_to)

    total_income = tx.filter(tx_type="income").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    total_expense = tx.filter(tx_type="expense").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    net_total = total_income - total_expense

    tx_form = VehicleTransactionForm(initial={"date": date.today()})

    return render(
        request,
        "assets/vehicle_detail.html",
        {
            "vehicle": vehicle,
            "transactions": tx,
            "tx_form": tx_form,
            "total_income": total_income,
            "total_expense": total_expense,
            "net_total": net_total,
            "date_from": date_from,
            "date_to": date_to,
        },
    )


@login_required
@has_any_group("Admin", "Accountant", "Staff")
def add_vehicle_transaction(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.method != "POST":
        return redirect("assets:vehicle_detail", vehicle_id=vehicle.id)

    form = VehicleTransactionForm(request.POST)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.vehicle = vehicle
        obj.created_by = request.user
        obj.save()
        return redirect("assets:vehicle_detail", vehicle_id=vehicle.id)

    # ✅ If invalid, re-render detail page and show form errors
    tx = vehicle.transactions.all()
    total_income = tx.filter(tx_type="income").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    total_expense = tx.filter(tx_type="expense").aggregate(s=Sum("amount"))["s"] or Decimal("0.00")
    net_total = total_income - total_expense

    return render(
        request,
        "assets/vehicle_detail.html",
        {
            "vehicle": vehicle,
            "transactions": tx,
            "tx_form": form,  # form with errors
            "total_income": total_income,
            "total_expense": total_expense,
            "net_total": net_total,
            "date_from": "",
            "date_to": "",
        },
        status=400,
    )


@login_required
@has_any_group("Admin", "Accountant", "Staff")
def tx_delete(request, tx_id):
    tx = get_object_or_404(VehicleTransaction, id=tx_id)
    vehicle_id = tx.vehicle.id

    if request.method == "POST":
        tx.delete()

    return redirect("assets:vehicle_detail", vehicle_id=vehicle_id)
