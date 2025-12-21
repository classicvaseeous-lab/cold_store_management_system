from django.urls import path
from . import views

urlpatterns = [
    path("", views.employees_list, name="employees_list"),
    path("add/", views.employee_create, name="employee_add"),
    path("<int:pk>/edit/", views.employee_edit, name="employee_edit"),
    path("<int:pk>/delete/", views.employee_delete, name="employee_delete"),

    path("attendance/", views.attendance_dashboard, name="attendance_dashboard"),
    path("attendance/<int:employee_id>/in/", views.clock_in, name="clock_in"),
    path("attendance/<int:employee_id>/out/", views.clock_out, name="clock_out"),
    # ✅ Staff self-attendance
    path("me/", views.my_attendance, name="my_attendance"),
    path("me/in/", views.my_clock_in, name="my_clock_in"),
    path("me/out/", views.my_clock_out, name="my_clock_out"),

]
