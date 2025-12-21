from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class BankAccount(models.Model):
    name = models.CharField(max_length=100)                 # e.g. Ecobank, MoMo, Cash Box
    account_number = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-is_active", "name"]

    def __str__(self):
        label = self.bank_name or "Account"
        return f"{self.name} ({label})"


class BankTransaction(models.Model):
    TYPES = [("credit", "Credit"), ("debit", "Debit")]

    account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name="transactions")
    tx_type = models.CharField(max_length=10, choices=TYPES)
    title = models.CharField(max_length=160)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    date = models.DateField()
    reference = models.CharField(max_length=80, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-id"]

    def __str__(self):
        return f"{self.account.name} - {self.tx_type} - ₵{self.amount}"
