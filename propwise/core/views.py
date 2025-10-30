# core/views.py

from django.shortcuts import render
from properties.models import Property       # Import our Property model
from properties.filters import PropertyFilter  # <-- 1. IMPORT YOUR FILTER

def homepage(request):
    """
    View for the homepage.
    Fetches the 12 most recent property listings.
    Also provides the filter form for the search box.
    """
    
    # This query is the same as before
    latest_properties = Property.objects.order_by('-created_at')[:12]
    
    # --- 2. CREATE AN INSTANCE OF THE FILTER ---
    # We create an unbound filter form to display on the page.
    # We don't pass 'request.GET' here, because we are not
    # *displaying* results on the homepage, just the form itself.
    filter_form = PropertyFilter()
    
    # --- 3. ADD THE FORM TO THE CONTEXT ---
    context = {
        'properties': latest_properties,
        'filter_form': filter_form  # <-- Pass the form to the template
    }
    
    return render(request, 'core/homepage.html', context)