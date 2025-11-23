from django.contrib import admin
from .models import Sale, SaleItem

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'payment_method', 'total_amount', 'timestamp')
    list_filter = ('payment_method', 'timestamp')
    search_fields = ('customer_name',)
    readonly_fields = ('total_amount', 'timestamp')

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'sale', 'product', 'quantity', 'unit_price', 'line_total')
    list_filter = ('sale', 'product')
    search_fields = ('product__name',)
    readonly_fields = ('line_total',)
