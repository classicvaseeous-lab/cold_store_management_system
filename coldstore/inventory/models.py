from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # retail price
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    quantity = models.IntegerField(default=0)  # current balance
    min_quantity_alert = models.IntegerField(default=5)
    image = models.ImageField(upload_to='products/', blank=True, null=True)   # <--- NEW
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.quantity})"

# class Product(models.Model):
#     name = models.CharField(max_length=200)
#     sku = models.CharField(max_length=100, blank=True, null=True)
#     category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
#     unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # retail price
#     wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     quantity = models.IntegerField(default=0)  # current balance
#     min_quantity_alert = models.IntegerField(default=5)
#     created_at = models.DateTimeField(auto_now_add=True)
#     created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # 👈 ADD THIS

    def __str__(self):
        return f"{self.name} ({self.quantity})"

class StockEntry(models.Model):
    """Stock-in (receiving)"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.quantity = self.product.quantity + self.quantity
        self.product.save()

class StockOut(models.Model):
    """Stock out: sold or disposed"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=200, choices=[("Sold","Sold"),("Disposed","Disposed"),("Transfer","Transfer")])
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.quantity = self.product.quantity - self.quantity
        if self.product.quantity < 0:
            self.product.quantity = 0
        self.product.save()
# class InventoryAdjustment(models.Model):   ask Chaggpt if is applicable
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     adjusted_quantity = models.IntegerField()
#     reason = models.TextField(blank=True)
#     adjusted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     adjusted_at = models.DateTimeField(auto_now_add=True)

#     def save(self, *args, **kwargs):
#         super().save(*args, **kwargs)
#         self.product.quantity = self.adjusted_quantity
#         self.product.save()