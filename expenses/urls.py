from django.urls import path
from . import views

urlpatterns = [
    path("add/", views.add_expense, name="add_expense"),
# added lines below by frank for expense listing and categories
    path("", views.expense_list, name="expense_list"),
    path("categories/", views.expense_category_list, name="expense_category_list"),
    path("categories/add/", views.add_expense_category, name="add_expense_category"),
    # example
 
    # path('<int:pk>/', views.expense_detail, name='expense_detail'),
]

