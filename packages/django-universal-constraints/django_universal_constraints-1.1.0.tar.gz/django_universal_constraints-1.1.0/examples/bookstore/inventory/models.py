"""
Inventory app models demonstrating universal constraints.

This module shows simplified inventory models with different constraint types
for the second_database (app-level validation only).
"""

from django.db import models
from django.db.models import Q, UniqueConstraint


class Location(models.Model):
    """
    Storage location model with non-conditional unique constraint.
    
    Business Rule: All location codes must be unique.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)
    
    class Meta:
        constraints = [
            # Non-conditional constraint: All location codes must be unique
            UniqueConstraint(
                fields=['code'],
                name='unique_location_code'
            )
        ]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Stock(models.Model):
    """
    Stock tracking model with conditional unique constraint.
    
    Business Rule: Each book can only have one active stock record per location.
    """
    # Using book_id instead of ForeignKey to avoid cross-database relations
    book_id = models.IntegerField()
    book_title = models.CharField(max_length=300)  # Cached for display
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        constraints = [
            # Conditional constraint: Each book can have only one active stock per location
            UniqueConstraint(
                fields=['book_id', 'location'],
                condition=Q(is_active=True),
                name='unique_active_stock'
            )
        ]
        ordering = ['book_title', 'location']
    
    def __str__(self):
        return f"{self.book_title} at {self.location.name} ({self.quantity} units)"
