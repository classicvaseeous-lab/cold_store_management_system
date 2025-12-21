from django import forms
from .models import Vehicle, VehicleTransaction

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ["name", "plate_number", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

 

class VehicleTransactionForm(forms.ModelForm):
    class Meta:
        model = VehicleTransaction
        fields = ["tx_type", "title", "amount", "date", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def clean_amount(self):
        amt = self.cleaned_data.get("amount")
        if amt is None or amt <= 0:
            raise forms.ValidationError("Amount must be greater than 0.")
        return amt
