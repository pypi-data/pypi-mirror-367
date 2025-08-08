"""
Customers app models demonstrating universal constraints.

This module shows simplified customer models with unique_together constraints
for the second_database (app-level validation only).
"""

from django.db import models


class Customer(models.Model):
    """
    Customer model with multiple unique_together constraints.
    
    Business Rules:
    1. Username + Email combination must be unique
    2. Phone numbers must be unique (single field unique_together)
    """
    username = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    class Meta:
        # Multiple unique_together constraints
        unique_together = [
            ('username', 'email'),  # Username + Email must be unique together
            ('phone',),             # Phone must be unique (single field unique_together)
        ]
        ordering = ['username']
    
    def __str__(self):
        return f"{self.username} ({self.email})"


class Order(models.Model):
    """
    Order model with unique_together constraint.
    
    Business Rule: Order number + Customer combination must be unique.
    """
    order_number = models.CharField(max_length=50)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        # unique_together: Order number + Customer must be unique
        unique_together = [('order_number', 'customer')]
        ordering = ['-id']
    
    def __str__(self):
        return f"Order {self.order_number} for {self.customer.username}"
