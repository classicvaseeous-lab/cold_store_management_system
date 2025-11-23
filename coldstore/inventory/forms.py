from django import forms
from .models import Product, StockEntry, StockOut

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

class StockEntryForm(forms.ModelForm):
    class Meta:
        model = StockEntry
        fields = ["product", "quantity", "unit_price", "notes"]

class StockOutForm(forms.ModelForm):
    class Meta:
        model = StockOut
        fields = ["product", "quantity", "reason"]
