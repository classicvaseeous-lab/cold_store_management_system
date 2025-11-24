from django.contrib import admin
from .models import Category, Product, StockEntry, StockOut

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(StockEntry)
admin.site.register(StockOut)
# admin.site.register(InventoryAdjustment)  # Uncomment if InventoryAdjustment model is used