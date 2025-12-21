from django.urls import path
from . import views

app_name = "assets"

urlpatterns = [
    path("", views.vehicle_list, name="vehicle_list"),
    path("add/", views.add_vehicle, name="add_vehicle"),
    path("<int:vehicle_id>/", views.vehicle_detail, name="vehicle_detail"),
    path("<int:vehicle_id>/tx/add/", views.add_vehicle_transaction, name="add_vehicle_transaction"),
    path("tx/<int:tx_id>/delete/", views.tx_delete, name="tx_delete"),
]
