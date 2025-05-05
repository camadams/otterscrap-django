from django.shortcuts import render
from django.http import JsonResponse
from .scraper import check_availability

# Create your views here if needed
def check_availability_view(request):
    """API endpoint to manually trigger availability check"""
    success, message = check_availability()
    
    return JsonResponse({
        'success': success,
        'message': message if message else 'No new availability found.'
    })
