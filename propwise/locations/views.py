# locations/views.py

from django.shortcuts import render, get_object_or_404
from .models import City, Area,Amenity
from properties.models import Property # We'll need this for Page 3 later
from django.http import JsonResponse
# locations/views.py 
from django.http import JsonResponse
import json


def all_cities_view(request):
    """
    Page 1: Displays a list of all cities.
    """
    # Get all City objects, ordered by name
    cities = City.objects.all().order_by('name')
    
    context = {
        'cities': cities
    }
    return render(request, 'locations/all_cities.html', context)


def city_detail_view(request, city_pk):
    """
    Page 2: Displays details for one city, including all its areas.
    """
    # Get the specific city, or show a 404 error
    city = get_object_or_404(City, pk=city_pk)
    
    # Get all areas related to this one city
    areas_in_city = city.areas.all().order_by('name')
    
    context = {
        'city': city,
        'areas': areas_in_city
    }
    return render(request, 'locations/city_detail.html', context)

# this si fo rarew show detaisls
# 


# locations/views.py

# --- REPLACE YOUR OLD 'area_detail_view' WITH THIS ---

# locations/views.py

# --- REPLACE YOUR OLD 'area_detail_view' WITH THIS ---

def area_detail_view(request, area_pk):
    """
    Page 3: Displays all properties for a specific area,
    PLUS the new "Neighborhood Insights" and "What's Nearby" data.
    """
    # 1. Get the specific area
    area = get_object_or_404(Area, pk=area_pk)
    
    # 2. Get all properties in this area
    properties_in_area = Property.objects.filter(area=area).order_by('-created_at')
    
    # 3. Get all amenities and group them by type (for the list)
    all_amenities = area.amenities.all().order_by('amenity_type', 'name')
    
    amenities_by_type = {}
    
    # --- 4. NEW: Create a JSON list of amenities *for the map* ---
    amenities_for_map = []
    
    for amenity in all_amenities:
        # Group amenities for the list display
        type_name = amenity.get_amenity_type_display()
        if type_name not in amenities_by_type:
            amenities_by_type[type_name] = []
        amenities_by_type[type_name].append(amenity)
        
        # Add amenity to the map list *only if* it has coordinates
      # ... (inside the 'for amenity in all_amenities:' loop)
        if amenity.latitude and amenity.longitude:
            
            # --- THIS IS THE UPGRADE ---
            # Call our new helper function
            map_details = amenity.get_map_details()

            amenities_for_map.append({
                'name': amenity.name,
                'type': amenity.get_amenity_type_display(),
                'lat': float(amenity.latitude),
                'lng': float(amenity.longitude),
                'icon': map_details['icon'],  # <-- Add the icon name
                'color': map_details['color'] # <-- Add the color
            })

    # --- 5. Build the final context ---
    context = {
        'area': area,
        'properties': properties_in_area,
        'amenities_by_type': amenities_by_type,
        
        # This is the new, safe JSON string for our JavaScript
        'amenities_json': json.dumps(amenities_for_map)
    }
    
    return render(request, 'locations/area_detail.html', context)


# locations/views.py (at the bottom for show only areas of city to create listing)

def ajax_load_areas(request):
    """
    An "API" view that returns a list of areas for a given city_id.
    Called by JavaScript to populate the 'Area' dropdown.
    """
    # Get the city_id from the 'GET' request's query parameters
    city_id = request.GET.get('city_id')

    if city_id:
        # Get all areas for that city
        areas = Area.objects.filter(city_id=city_id).order_by('name')

        # Format the data as a list of simple objects
        # Our JavaScript will expect 'id' and 'name'
        data = [{'id': area.id, 'name': area.name} for area in areas]

        # Return the data as a JSON response
        return JsonResponse(data, safe=False)

    # If no city_id is provided, return an empty list
    return JsonResponse([], safe=False)