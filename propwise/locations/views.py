# locations/views.py

from django.shortcuts import render, get_object_or_404
from .models import City, Area
from properties.models import Property # We'll need this for Page 3 later

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