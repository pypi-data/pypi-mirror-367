"""
Django admin configuration for books app.

This demonstrates how universal_constraints works seamlessly with Django admin.
"""

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.contrib import messages
from .models import Author, Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'email']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'email', 'is_active')
        }),
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn']
    list_filter = ['author']
    search_fields = ['title', 'isbn', 'author__name']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'author', 'isbn')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Custom save method that demonstrates how constraint validation
        works in Django admin. The universal_constraints library will
        automatically validate universal constraints.
        """
        try:
            super().save_model(request, obj, form, change)
            if not change:  # New object
                messages.success(
                    request, 
                    f'Book "{obj.title}" was created successfully. '
                    f'Universal constraints were validated automatically.'
                )
        except ValidationError as e:
            # This will be caught by Django admin and displayed as form errors
            messages.error(
                request,
                f'Validation error: {e.message}'
            )
            raise


# Customize the admin site header
admin.site.site_header = "Bookstore Administration"
admin.site.site_title = "Bookstore Admin"
admin.site.index_title = "Welcome to Bookstore Administration"
