"""
Books app models demonstrating universal constraints.

This module shows simplified examples of different constraint types
for the bookstore demo using the universal_constraints library.
"""

from django.db import models
from django.db.models import Q, UniqueConstraint


class Author(models.Model):
    """
    Author model with conditional unique email constraint.
    
    Business Rule: Active authors must have unique email addresses.
    """
    name = models.CharField(max_length=200)
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        constraints = [
            # Conditional constraint: Active authors must have unique emails
            UniqueConstraint(
                fields=['email'],
                condition=Q(is_active=True),
                name='unique_active_author_email'
            )
        ]
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({'active' if self.is_active else 'inactive'})"


class Book(models.Model):
    """
    Book model with non-conditional constraint and unique_together.
    
    Business Rules:
    1. All books must have unique ISBNs (non-conditional)
    2. Title + Author combination must be unique (unique_together)
    """
    title = models.CharField(max_length=300)
    isbn = models.CharField(max_length=17)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    
    class Meta:
        constraints = [
            # Non-conditional constraint: All ISBNs must be unique
            UniqueConstraint(
                fields=['isbn'],
                name='unique_isbn'
            )
        ]
        # unique_together: Title + Author must be unique
        unique_together = [('title', 'author')]
        ordering = ['title']
    
    def __str__(self):
        return f"{self.title} by {self.author.name}"
