# core/views.py

from django.shortcuts import render
from properties.models import Property       # Import our Property model
from properties.filters import PropertyFilter  # Import your filter
from django.utils import timezone  # <-- 1. IMPORT 'timezone'

def homepage(request):
    """
    View for the homepage.
    
    NOW UPGRADED:
    1. Fetches all *FEATURED* properties for the top slider.
    2. Fetches the 12 most recent *VERIFIED, NON-FEATURED* properties.
    3. Provides the filter form for the search box.
    """
    
    # --- 2. NEW: "FEATURED" PROPERTIES QUERY ---
    # This is your monetization.
    # We find all properties that are:
    #   a) Marked as 'is_featured'
    #   b) Not expired (their 'featured_until' date is in the future)
    
    # Get the current time
    now = timezone.now()
    
    featured_properties = Property.objects.filter(
        is_verified=True,     # Must be verified
        is_featured=True,     # Must be featured
        featured_until__gte=now  # Must not be expired
    ).order_by('-created_at') # Show newest featured first
    
    
    # --- 3. UPGRADED: "LATEST" PROPERTIES QUERY ---
    # We now filter for 'is_verified=True' AND 'is_featured=False'
    # to avoid showing the same properties in both sections.
    latest_properties = Property.objects.filter(
        is_verified=True,
        is_featured=False
    ).order_by('-created_at')[:12]
    
    
    # This logic for the filter form is perfect as-is
    filter_form = PropertyFilter()
    
    # --- 4. ADD BOTH LISTS TO THE CONTEXT ---
    context = {
        'featured_properties': featured_properties, # <-- Your new list
        'latest_properties': latest_properties,   # <-- Your upgraded list
        'filter_form': filter_form
    }
    
    return render(request, 'core/homepage.html', context)