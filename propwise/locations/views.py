# locations/views.py

from django.shortcuts import render, get_object_or_404
from .models import City, Area
from properties.models import Property # We'll need this for Page 3 later
from django.http import JsonResponse
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


def area_detail_view(request, area_pk):
    """
    Page 3: Displays all properties for a specific area.
    """
    # Get the specific area, or show a 404 error
    area = get_object_or_404(Area, pk=area_pk)
    
    # --- THIS IS THE KEY ---
    # We find all properties that have a foreign key
    # pointing to this specific 'area' object.
    properties_in_area = Property.objects.filter(area=area).order_by('-created_at')
    
    context = {
        'area': area,
        'properties': properties_in_area  # We pass the list of properties to the template
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