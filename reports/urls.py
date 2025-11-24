# from django.urls import path
# from . import views

# urlpatterns = [
#     path("", views.summary, name="reports_summary"),
#     path("export/sales/", views.export_sales_csv, name="export_sales_csv"),
#     path("export/expenses/", views.export_expenses_csv, name="export_expenses_csv"),
# ]

# reports/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.summary, name="reports_summary"),
    path("export/sales/csv/", views.export_sales_csv, name="export_sales_csv"),
    path("export/sales/excel/", views.export_sales_excel, name="export_sales_excel"),
    path("export/sales/pdf/", views.export_sales_pdf, name="export_sales_pdf"),
    path("api/chart-sales-expenses/", views.chart_sales_vs_expenses, name="chart_sales_vs_expenses"),
]
