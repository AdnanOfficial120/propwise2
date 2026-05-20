# core/views.py

from django.shortcuts import render
# --- 1. IMPORT PropertyStatus ---
from properties.models import Property, PropertyStatus 
from properties.filters import PropertyFilter
from django.utils import timezone

# core/views.py
 
def homepage(request):
    """
    View for the homepage.
    NOW UPGRADED WITH AJAX FILTERING.
    """
    now = timezone.now()
    
    featured_properties = Property.objects.filter(
        is_verified=True,
        is_featured=True,
        featured_until__gte=now,
        status=PropertyStatus.ACTIVE 
    ).order_by('-created_at')
    
    # 1. Start with the base query for the latest properties
    latest_qs = Property.objects.filter(
        is_verified=True,
        is_featured=False,
        status=PropertyStatus.ACTIVE
    ).order_by('-created_at')

    # 2. Check if a specific category was clicked
    category = request.GET.get('category')
    if category:
        latest_qs = latest_qs.filter(property_type=category)

    latest_properties = latest_qs[:12]

    # 3. If this is an AJAX request from our JavaScript, ONLY return the property cards
    if request.GET.get('ajax') == 'true':
        return render(request, 'core/property_grid.html', {'latest_properties': latest_properties})
    
    # 4. Otherwise, load the full page normally
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

