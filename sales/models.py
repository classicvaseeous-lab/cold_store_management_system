
# sales/models.py
from django.db import models
from django.contrib.auth.models import User
from inventory.models import Product
from decimal import Decimal

class Sale(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('momo', 'Mobile Money'),
        ('card', 'Card'),
    ]

    SALE_TYPES = [
        ("retail", "Retail"),
        ("wholesale", "Wholesale"),
    ]

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    sale_type = models.CharField(max_length=20, choices=SALE_TYPES, default="retail")  # ✅ NEW

    customer_name = models.CharField(max_length=100, blank=True, null=True)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')

    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    subtotal_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))  # ✅ NEW
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))       # ✅ NEW
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))     # = GRAND TOTAL

    note = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_sale_type_display()} Sale #{self.id} - ₵{self.total_amount}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def line_total(self):
        qty = self.quantity or 0
        price = self.unit_price or Decimal("0.00")
        return Decimal(qty) * Decimal(price)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # ✅ Only adjust inventory here (DO NOT update sale.total_amount here)
        if self.product:
            self.product.quantity = max(0, self.product.quantity - self.quantity)
            self.product.save()
         # update sale total after saving items
        sale_total = sum(item.line_total() for item in self.sale.items.all())
        self.sale.total_amount = sale_total
        self.sale.save()
        
    def __str__(self):
        pname = self.product.name if self.product else "Deleted Product"
        return f"{pname} x {self.quantity} @ {self.unit_price}"




# from django.db import models
# from django.contrib.auth.models import User
# from inventory.models import Product

# class Sale(models.Model):
#     PAYMENT_METHODS = [
#         ('cash', 'Cash'),
#         ('momo', 'Mobile Money'),
#         ('card', 'Card'),
#     ]

#     created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     customer_name = models.CharField(max_length=100, blank=True, null=True)
#     payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
#     customer_phone = models.CharField(max_length=15, blank=True, null=True)
#     discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     note = models.TextField(blank=True)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Sale #{self.id} - ₵{self.total_amount}"

# class SaleItem(models.Model):
#     sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
#     product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
#     quantity = models.IntegerField()
#     unit_price = models.DecimalField(max_digits=10, decimal_places=2)

#     def line_total(self):
#         qty = self.quantity or 0
#         price = self.unit_price or 0
#         return qty * price

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)

#         # decrease inventory
#         if self.product:
#             self.product.quantity = max(0, self.product.quantity - self.quantity)
#             self.product.save()

#         # update sale total after saving items
#         sale_total = sum(item.line_total() for item in self.sale.items.all())
#         self.sale.total_amount = sale_total
#         self.sale.save()

#     def __str__(self):
#         return f"{self.product.name if self.product else 'Deleted Product'} x {self.quantity} @ {self.unit_price}"


# class SaleItem(models.Model):
#     sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
#     product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
#     quantity = models.IntegerField()
#     unit_price = models.DecimalField(max_digits=10, decimal_places=2)

#     def line_total(self):
#         return self.quantity*self.unit_price

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         # decrease inventory
#         if self.product:
#             self.product.quantity = max(0, self.product.quantity - self.quantity)
#             self.product.save()

#         # update sale total amount after each item save
#         sale_total = sum(item.line_total() for item in self.sale.items.all())
#         self.sale.total_amount = sale_total
#         self.sale.save()

#     def __str__(self):
#         return f"{self.product.name if self.product else 'Deleted Product'} x {self.quantity} @ {self.unit_price}"
