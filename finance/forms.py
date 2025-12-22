from django import forms
from .models import BankAccount, BankTransaction
from decimal import Decimal

class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        fields = ["name", "bank_name", "account_number", "opening_balance", "is_active", "notes"]

    def clean_opening_balance(self):
        bal = self.cleaned_data.get("opening_balance")
        return bal if bal is not None else Decimal("0.00")


class BankTransactionForm(forms.ModelForm):
    class Meta:
        model = BankTransaction
        fields = ["tx_type", "date", "title", "amount", "reference", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def clean_amount(self):
        amt = self.cleaned_data.get("amount")
        if amt is None or amt <= 0:
            raise forms.ValidationError("Amount must be greater than 0.")
        return amt



