"""
Django admin configuration for customers app.
"""

from django.contrib import admin
from .models import Customer, Order


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone']
    search_fields = ['username', 'email', 'phone']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'customer', 'total_amount']
    list_filter = ['customer']
    search_fields = ['order_number', 'customer__username']
