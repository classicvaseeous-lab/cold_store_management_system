from django.urls import path
from . import views

app_name = "finance"

urlpatterns = [
    path("", views.account_list, name="account_list"),
    path("account/add/", views.account_create, name="account_create"),
    path("account/<int:account_id>/edit/", views.account_edit, name="account_edit"),

    path("account/<int:account_id>/", views.account_detail, name="account_detail"),
    path("account/<int:account_id>/tx/add/", views.tx_add, name="tx_add"),

    path("tx/<int:tx_id>/delete/", views.tx_delete, name="tx_delete"),
]
