"""
URL configuration for inventory app.
"""

from django.urls import path
from django.http import HttpResponse

app_name = 'inventory'

def placeholder_view(request):
    return HttpResponse("Inventory app placeholder - check Django admin for inventory management")

urlpatterns = [
    path('', placeholder_view, name='index'),
]
