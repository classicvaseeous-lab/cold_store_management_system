from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User


class Vehicle(models.Model):
    name = models.CharField(max_length=100)
    plate_number = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.plate_number})"


class VehicleTransaction(models.Model):
    TYPES = [("income", "Income"), ("expense", "Expense")]

    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="transactions"
    )
    tx_type = models.CharField(max_length=10, choices=TYPES)
    title = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    date = models.DateField()
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.vehicle} - {self.tx_type} - ₵{self.amount}"
