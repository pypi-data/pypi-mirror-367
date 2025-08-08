"""
Django admin configuration for inventory app.
"""

from django.contrib import admin
from .models import Location, Stock


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['book_title', 'location', 'quantity', 'is_active']
    list_filter = ['location', 'is_active']
    search_fields = ['book_title', 'location__name']
