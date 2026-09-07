from django.contrib import admin

from .models import CustomerProfile, Order, Product, SellerProfile


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('shop_name', 'user', 'phone_number', 'created_at')
    search_fields = ('shop_name', 'user__username')


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'created_at')
    search_fields = ('user__username',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'seller', 'original_price', 'discounted_price',
        'commission_percent', 'quantity_available', 'expiry_date', 'is_active',
    )
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'seller__shop_name')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'product', 'customer', 'seller', 'quantity',
        'total_price', 'commission_amount_total', 'seller_earning_total',
        'status', 'created_at',
    )
    list_filter = ('status',)
    search_fields = ('product__name', 'customer__user__username', 'seller__shop_name')
