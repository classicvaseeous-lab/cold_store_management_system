from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    TRACK_METHODS = [
        
        ("unit", "Unit (normal)"),
        ("boxed_weight", "Boxed Weight (e.g. 30kg box)"),
    ]
    track_method = models.CharField(max_length=20, choices=TRACK_METHODS, default="unit")
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # retail price
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    # ✅ BOX + WEIGHT STOCK
    box_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    # ✅ Weight-based (boxed) settings
    is_weighted = models.BooleanField(default=False)
    boxes_in_stock = models.IntegerField(default=0)
    box_remaining_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    quantity = models.IntegerField(default=0)  # current balance
    min_quantity_alert = models.IntegerField(default=5)
    image = models.ImageField(upload_to='products/', blank=True, null=True)   # <--- NEW
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    def available_weight_kg(self):
        """
        If weighted:
        total remaining = (boxes_in_stock-1)*box_weight + box_remaining (when box_remaining < box_weight)
        If box_remaining == box_weight (fresh), total = boxes_in_stock*box_weight
        """
        """Calculate total available weight in kg for weighted products."""
        if not self.is_weighted or self.boxes_in_stock <= 0 or self.box_weight_kg <= 0:
            return Decimal("0.00")

        bw = Decimal(self.box_weight_kg or Decimal("0.00"))
        br = Decimal(self.box_remaining_kg or Decimal("0.00"))
    # If not initialized yet, treat as full current box
        # if br <= 0:
        #     br = bw
         # safety
        if br < 0:
            br = Decimal("0.00")

        # if not initialized yet and boxes exist, treat as full current box
        if br == 0 and self.boxes_in_stock > 0:
            br = bw

        total = (Decimal(max(self.boxes_in_stock - 1, 0)) * bw) + br
        return total.quantize(Decimal("0.01"))

    def __str__(self):
        return self.name

 
class ProductWeightPrice(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="weight_prices")
    weight_kg = models.DecimalField(max_digits=8, decimal_places=2)   # e.g. 5.00, 10.00, 30.00
    retail_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    wholesale_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("product", "weight_kg")
        ordering = ["weight_kg"]

    def __str__(self):
        return f"{self.product.name} - {self.weight_kg}kg"


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



"""
✅ Here is the CLEAN corrected version of your inventory/models.py (copy & replace)
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    TRACK_METHODS = [
        ("unit", "Unit (normal)"),
        ("boxed_weight", "Boxed Weight (e.g. 30kg box)"),
    ]

    track_method = models.CharField(max_length=20, choices=TRACK_METHODS, default="unit")
    box_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=100, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    unit_price = models.DecimalField(max_digits=10, decimal_places=2)  # retail price
    wholesale_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    quantity = models.IntegerField(default=0)  # normal unit stock
    min_quantity_alert = models.IntegerField(default=5)

    image = models.ImageField(upload_to="products/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.quantity})"


class StockReceipt(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="receipts")
    boxes_received = models.PositiveIntegerField(default=0)
    box_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    received_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Receipt #{self.id} {self.product.name} — {self.boxes_received} boxes"


class StockBox(models.Model):
    receipt = models.ForeignKey(StockReceipt, on_delete=models.CASCADE, related_name="boxes")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stock_boxes")

    capacity_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    remaining_kg = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    created_on = models.DateTimeField(auto_now_add=True)
    consumed_on = models.DateTimeField(null=True, blank=True)

    @property
    def is_consumed(self):
        return (self.remaining_kg or Decimal("0.00")) <= Decimal("0.00")

    def __str__(self):
        return f"{self.product.name} Box #{self.id} — {self.remaining_kg}/{self.capacity_kg}kg"


class SaleableWeightSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="weight_sizes")
    size_kg = models.DecimalField(max_digits=10, decimal_places=2)

    retail_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    wholesale_price = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        unique_together = ("product", "size_kg")
        ordering = ["size_kg"]

    def __str__(self):
        return f"{self.product.name} — {self.size_kg}kg"


class WeightSizeAllocation(models.Model):
    size = models.OneToOneField(SaleableWeightSize, on_delete=models.CASCADE, related_name="allocation")
    current_box = models.ForeignKey(StockBox, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Allocation for {self.size}"


class StockEntry(models.Model):
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
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    reason = models.CharField(
        max_length=200,
        choices=[("Sold", "Sold"), ("Disposed", "Disposed"), ("Transfer", "Transfer")]
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.quantity = self.product.quantity - self.quantity
        if self.product.quantity < 0:
            self.product.quantity = 0
        self.product.save()
    """