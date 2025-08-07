"""
URL configuration for customers app.
"""

from django.urls import path
from django.http import HttpResponse

app_name = 'customers'

def placeholder_view(request):
    return HttpResponse("Customers app placeholder - check Django admin for customer management")

urlpatterns = [
    path('', placeholder_view, name='index'),
]
