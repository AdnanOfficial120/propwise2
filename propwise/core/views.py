# core/views.py

from django.shortcuts import render
# --- 1. IMPORT PropertyStatus ---
from properties.models import Property, PropertyStatus 
from properties.filters import PropertyFilter
from django.utils import timezone

def homepage(request):
    """
    View for the homepage.
    NOW UPGRADED:
    1. Fetches all *ACTIVE, FEATURED* properties for the top slider.
    2. Fetches the 12 most recent *ACTIVE, VERIFIED, NON-FEATURED* properties.
    3. Provides the filter form for the search box.
    """
    
    now = timezone.now()
    
    featured_properties = Property.objects.filter(
        is_verified=True,
        is_featured=True,
        featured_until__gte=now,
        status=PropertyStatus.ACTIVE  # <-- 2. ADD THIS FILTER
    ).order_by('-created_at')
    
    
    latest_properties = Property.objects.filter(
        is_verified=True,
        is_featured=False,
        status=PropertyStatus.ACTIVE  # <-- 3. ADD THIS FILTER
    ).order_by('-created_at')[:12]
    
    
    # This logic for the filter form is perfect as-is
    filter_form = PropertyFilter()
    
    context = {
        'featured_properties': featured_properties,
        'latest_properties': latest_properties,
        'filter_form': filter_form
    }
    
    return render(request, 'core/homepage.html', context)


# core/views.py for calculator

def calculator_view(request):
    """
    Renders the new Mortgage/Affordability Calculator page.
    The page itself is mostly HTML and JavaScript.
    """
    # We will create this template in the next step
    return render(request, 'core/calculator.html')

