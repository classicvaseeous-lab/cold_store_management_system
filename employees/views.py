from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q

from users.utils import has_any_group
from .models import EmployeeProfile, AttendanceLog
from .forms import EmployeeProfileForm


@login_required
@has_any_group("Admin")
def employees_list(request):
    q = request.GET.get("q", "").strip()
    employees = EmployeeProfile.objects.select_related("user").all().order_by("full_name")

    if q:
        employees = employees.filter(
            Q(full_name__icontains=q)
            | Q(phone__icontains=q)
            | Q(user__username__icontains=q)
            | Q(user__email__icontains=q)
        )

    return render(request, "employees/employees_list.html", {"employees": employees, "q": q})


@login_required
@has_any_group("Admin")
def employee_create(request):
    if request.method == "POST":
        form = EmployeeProfileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Employee added successfully.")
            return redirect("employees_list")
        messages.error(request, "❌ Please fix the errors and try again.")
    else:
        form = EmployeeProfileForm()

    return render(request, "employees/employee_form.html", {"form": form, "title": "Add Employee"})


@login_required
@has_any_group("Admin")
def employee_edit(request, pk):
    emp = get_object_or_404(EmployeeProfile, pk=pk)
    if request.method == "POST":
        form = EmployeeProfileForm(request.POST, request.FILES, instance=emp)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Employee updated successfully.")
            return redirect("employees_list")
        messages.error(request, "❌ Please fix the errors and try again.")
    else:
        form = EmployeeProfileForm(instance=emp)

    return render(request, "employees/employee_form.html", {"form": form, "title": "Edit Employee"})


@login_required
@has_any_group("Admin")
def employee_delete(request, pk):
    emp = get_object_or_404(EmployeeProfile, pk=pk)
    if request.method == "POST":
        emp.delete()
        messages.success(request, "🗑️ Employee deleted.")
        return redirect("employees_list")

    return render(request, "employees/employee_confirm_delete.html", {"employee": emp})


@login_required
@has_any_group("Admin")
def attendance_dashboard(request):
    # latest 50 logs
    logs = AttendanceLog.objects.select_related("employee").all()[:50]

    # who is currently clocked-in (has open session)
    active_ids = AttendanceLog.objects.filter(clock_out__isnull=True).values_list("employee_id", flat=True)
    active_ids = set(active_ids)

    employees = EmployeeProfile.objects.all().order_by("full_name")

    return render(
        request,
        "employees/attendance_dashboard.html",
        {"employees": employees, "logs": logs, "active_ids": active_ids},
    )


@login_required
@has_any_group("Admin")
def clock_in(request, employee_id):
    emp = get_object_or_404(EmployeeProfile, id=employee_id)

    # prevent multiple open sessions
    if AttendanceLog.objects.filter(employee=emp, clock_out__isnull=True).exists():
        messages.error(request, f"⚠️ {emp.full_name} is already clocked in.")
        return redirect("attendance_dashboard")

    AttendanceLog.objects.create(employee=emp, clock_in=timezone.now())
    messages.success(request, f"✅ Clock-in recorded for {emp.full_name}.")
    return redirect("attendance_dashboard")


@login_required
@has_any_group("Admin")
def clock_out(request, employee_id):
    emp = get_object_or_404(EmployeeProfile, id=employee_id)

    log = AttendanceLog.objects.filter(employee=emp, clock_out__isnull=True).order_by("-clock_in").first()
    if not log:
        messages.error(request, f"⚠️ {emp.full_name} has no active clock-in to close.")
        return redirect("attendance_dashboard")

    log.clock_out = timezone.now()
    log.save()

    messages.success(request, f"✅ Clock-out recorded for {emp.full_name}.")
    return redirect("attendance_dashboard")




# to get user profile when login automatically

def _get_my_profile(request):
    # user must have EmployeeProfile linked
    if hasattr(request.user, "employee_profile"):
        return request.user.employee_profile
    return None


@login_required
@has_any_group("Admin", "Staff")
def my_attendance(request):
    emp = _get_my_profile(request)
    if not emp:
        messages.error(request, "⚠️ No employee profile is linked to your account. Contact Admin.")
        return redirect("inventory_dashboard")

    logs = emp.attendance.all()[:50]
    is_clocked_in = emp.attendance.filter(clock_out__isnull=True).exists()

    return render(request, "employees/my_attendance.html", {
        "employee": emp,
        "logs": logs,
        "is_clocked_in": is_clocked_in,
    })


@login_required
@has_any_group("Admin", "Staff")
def my_clock_in(request):
    emp = _get_my_profile(request)
    if not emp:
        messages.error(request, "⚠️ No employee profile is linked to your account. Contact Admin.")
        return redirect("inventory_dashboard")

    if AttendanceLog.objects.filter(employee=emp, clock_out__isnull=True).exists():
        messages.error(request, "⚠️ You are already clocked in.")
        return redirect("my_attendance")

    AttendanceLog.objects.create(employee=emp, clock_in=timezone.now())
    messages.success(request, "✅ Clock-in recorded.")
    return redirect("my_attendance")


@login_required
@has_any_group("Admin", "Staff")
def my_clock_out(request):
    emp = _get_my_profile(request)
    if not emp:
        messages.error(request, "⚠️ No employee profile is linked to your account. Contact Admin.")
        return redirect("inventory_dashboard")

    log = AttendanceLog.objects.filter(employee=emp, clock_out__isnull=True).order_by("-clock_in").first()
    if not log:
        messages.error(request, "⚠️ You have no active clock-in to close.")
        return redirect("my_attendance")

    log.clock_out = timezone.now()
    log.save()
    messages.success(request, "✅ Clock-out recorded.")
    return redirect("my_attendance")
