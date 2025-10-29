# core/views.py

from django.shortcuts import render
from properties.models import Property  # Import our Property model

def homepage(request):
    """
    View for the homepage.
    Fetches the 12 most recent property listings.
    """
    
    # We query the Property model, order by the newest first, 
    # and take the first 12.
    latest_properties = Property.objects.order_by('-created_at')[:12]
    
    # We create a "context" dictionary to send this data to our HTML template.
    context = {
        'properties': latest_properties
    }
    
    # We render the 'homepage.html' template and pass it the context.
    return render(request, 'core/homepage.html', context)