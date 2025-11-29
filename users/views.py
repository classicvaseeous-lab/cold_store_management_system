# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group

# @login_required
def dashboard_view(request):
    """
    Simple dashboard view for logged-in users.
    """
    return render(request, "users/dashboard.html")


# Optional helper (uncomment and wire into a custom LoginView if you want role-based redirects)
def redirect_by_role(user):
    """
    Example role-based redirect logic:
    - Admin -> reports
    - Accountant -> reports
    - Staff -> inventory dashboard
    """
    if user.is_superuser:
        return "reports_summary"
    if user.groups.filter(name="Accountant").exists():
        return "reports_summary"
    if user.groups.filter(name="Staff").exists():
        return "inventory_dashboard"
    return "inventory_dashboard"




# # users/views.py
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required

# @login_required
# def dashboard(request):
#     return render(request, "users/dashboard.html")
