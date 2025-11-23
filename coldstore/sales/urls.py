from django.urls import path
from . import views

urlpatterns = [
path("create/", views.create_sale, name="create_sale"),
path("sales/", views.sale_list, name="sale_list"),
path("sales/create/", views.create_sale, name="create_sale"),
path("sales/receipt/<int:sale_id>/", views.sale_receipt, name="sale_receipt"),
path("receipt/<int:sale_id>/", views.receipt_view, name="receipt_view"),

]
