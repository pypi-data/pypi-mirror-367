"""
URL configuration for books app.
"""

from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    # Book views
    path('', views.book_list, name='book_list'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    
    # Author views
    path('authors/', views.author_list, name='author_list'),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    
    # Constraint demonstration
    path('constraints/', views.constraint_demo, name='constraint_demo'),
    path('api/test-constraint/', views.api_test_constraint, name='api_test_constraint'),
]
