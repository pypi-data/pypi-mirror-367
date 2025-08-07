"""
Views for the books app.

Simple views to demonstrate the bookstore functionality.
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from .models import Book, Author


def book_list(request):
    """Display a list of books."""
    books = Book.objects.all().select_related('author')
    return render(request, 'books/book_list.html', {'books': books})


def book_detail(request, book_id):
    """Display details of a specific book."""
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'books/book_detail.html', {'book': book})


def author_list(request):
    """Display a list of active authors."""
    authors = Author.objects.filter(is_active=True)
    return render(request, 'books/author_list.html', {'authors': authors})


def author_detail(request, author_id):
    """Display details of a specific author."""
    author = get_object_or_404(Author, id=author_id)
    books = author.books.all()
    return render(request, 'books/author_detail.html', {
        'author': author,
        'books': books
    })


def constraint_demo(request):
    """
    Demonstration view showing how universal constraints work.
    
    This view provides examples of constraint validation in action.
    """
    context = {
        'examples': [
            {
                'title': 'Author Email Uniqueness',
                'description': 'Active authors must have unique emails.',
                'model': 'Author',
                'constraint': 'unique_active_author_email'
            },
            {
                'title': 'Book ISBN Uniqueness',
                'description': 'All books must have unique ISBNs.',
                'model': 'Book',
                'constraint': 'unique_isbn'
            },
            {
                'title': 'Book Title per Author',
                'description': 'Book titles must be unique per author.',
                'model': 'Book',
                'constraint': 'unique_together: title + author'
            }
        ]
    }
    return render(request, 'books/constraint_demo.html', context)


def api_test_constraint(request):
    """
    API endpoint to test constraint validation.
    
    This demonstrates how constraints work programmatically.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    test_type = request.POST.get('test_type')
    
    try:
        if test_type == 'author_email':
            # Test author email uniqueness
            author1 = Author.objects.create(
                name='Test Author 1',
                email='test@example.com',
                is_active=True
            )
            
            # This should fail due to unique constraint
            author2 = Author(
                name='Test Author 2',
                email='test@example.com',
                is_active=True
            )
            author2.save()  # This will raise ValidationError
            
        elif test_type == 'book_isbn':
            # Test book ISBN uniqueness
            author = Author.objects.create(
                name='Test Author',
                email='author@example.com',
                is_active=True
            )
            
            book1 = Book.objects.create(
                title='Test Book 1',
                isbn='978-0-123-45678-9',
                author=author
            )
            
            # This should fail due to unique constraint
            book2 = Book(
                title='Test Book 2',
                isbn='978-0-123-45678-9',
                author=author
            )
            book2.save()  # This will raise ValidationError
            
        return JsonResponse({'success': True, 'message': 'Test completed successfully'})
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'error': 'Constraint validation failed (as expected)',
            'details': str(e)
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Unexpected error',
            'details': str(e)
        }, status=500)
