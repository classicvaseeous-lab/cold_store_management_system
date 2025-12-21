from django.urls import path
from . import views

# app_name = "finance"

urlpatterns = [
    path("", views.account_list, name="account_list"),
    path("<int:account_id>/", views.account_detail, name="account_detail"),
    path("<int:account_id>/tx/add/", views.tx_add, name="tx_add"),
    path("tx/<int:tx_id>/delete/", views.tx_delete, name="tx_delete"),
]
