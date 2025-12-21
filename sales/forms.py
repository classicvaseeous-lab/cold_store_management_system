# sales/forms.py
from django import forms
from .models import Sale, SaleItem
from inventory.models import Product

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ["customer_name", "customer_phone", "payment_method", "discount"]

class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ["product", "quantity", "unit_price"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["product"].widget.attrs.update({
            "class": "product-select w-full rounded-lg p-2"
        })
        self.fields["quantity"].widget.attrs.update({
            "class": "qty-input w-full rounded-lg p-2"
        })
        self.fields["unit_price"].widget.attrs.update({
            "class": "price-input w-full rounded-lg p-2",
            "readonly": "readonly"
        })

        self.fields["product"].queryset = Product.objects.all()
        self.fields["product"].label_from_instance = (
            lambda obj: f"{obj.name} (Stock: {obj.quantity})"
        )

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get("product")
        qty = cleaned.get("quantity")

        if product and qty and qty > product.quantity:
            raise forms.ValidationError(f"Not enough stock! Available: {product.quantity}")

        return cleaned

# from django import forms
# from .models import Sale, SaleItem
# from inventory.models import Product


# class SaleForm(forms.ModelForm):
#     class Meta:
#         model = Sale
#         fields = ["customer_name", "customer_phone", "payment_method", "discount"]


# class SaleItemForm(forms.ModelForm):
#     class Meta:
#         model = SaleItem
#         fields = ["product", "quantity", "unit_price"]

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         # Add CSS classes to fields (needed for the JS auto-calculation)
#         self.fields["product"].widget.attrs.update({
#             "class": "product-select w-full rounded-lg p-2"
#         })
#         self.fields["quantity"].widget.attrs.update({
#             "class": "qty-input w-full rounded-lg p-2"
#         })
#         self.fields["unit_price"].widget.attrs.update({
#             "class": "price-input w-full rounded-lg p-2",
#             "readonly": "readonly"   # user should NOT type price manually
#         })

#         # Show product name + stock remaining inside dropdown
#         self.fields["product"].queryset = Product.objects.all()
#         self.fields["product"].label_from_instance = (
#             lambda obj: f"{obj.name} (Stock: {obj.quantity})"
#         )

#     def clean(self):
#         cleaned = super().clean()
#         product = cleaned.get("product")
#         qty = cleaned.get("quantity")

#         # Stock validation
#         if product and qty:
#             if qty > product.quantity:
#                 raise forms.ValidationError(
#                     f"Not enough stock! Available: {product.quantity}"
#                 )
#         return cleaned


# from django import forms
# from .models import Sale, SaleItem
# from inventory.models import Product

# class SaleForm(forms.ModelForm):
#     class Meta:
#         model = Sale

#         fields = ["customer_name", "payment_method", "customer_phone", "discount"]
#         # fields = ["note", "customer_name", "payment_method", "total_amount"] first version without note and it was removed later however for the first time it was only note
# class SaleItemForm(forms.ModelForm):
#     class Meta:
#         model = SaleItem
#         fields = ["product", "quantity", "unit_price"]

#     def clean(self):
#         cleaned = super().clean()
#         product = cleaned.get("product")
#         qty = cleaned.get("quantity")

#         if product and qty:
#             if qty > product.quantity:
#                 raise forms.ValidationError(f"Not enough stock! Available: {product.quantity}")

#         return cleaned

# class SaleItemForm(forms.ModelForm):
#     class Meta:
#         model = SaleItem
#         fields = ["product", "quantity", "unit_price"]
