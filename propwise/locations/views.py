# locations/views.py

from django.shortcuts import render, get_object_or_404
from .models import City, Area, Amenity
# --- 1. ADD PropertyStatus, Avg, TruncMonth ---
from properties.models import Property, PropertyStatus 
from django.http import JsonResponse
import json
from django.db.models import Avg
from django.db.models.functions import TruncMonth
from django.utils import timezone
import datetime
# locations/views.py (at the top)
from django.db.models import F, Case, When, DecimalField
from decimal import Decimal

def all_cities_view(request):
    """
    Page 1: Displays a list of all cities.
    """
    cities = City.objects.all().order_by('name')
    context = {
        'cities': cities
    }
    return render(request, 'locations/all_cities.html', context)


def city_detail_view(request, city_pk):
    """
    Page 2: Displays details for one city, including all its areas.
    """
    city = get_object_or_404(City, pk=city_pk)
    areas_in_city = city.areas.all().order_by('name')
    context = {
        'city': city,
        'areas': areas_in_city
    }
    return render(request, 'locations/city_detail.html', context)


# --- THIS IS YOUR NEW, FULLY UPGRADED VIEW ---
# locations/views.py

# locations/views.py

# locations/views.py

# --- REPLACE YOUR 'area_detail_view' FUNCTION WITH THIS ---

# locations/views.py

def area_detail_view(request, area_pk):
    """
    Page 3: Displays all properties for a specific area,
    PLUS Neighborhood Insights, "What's Nearby" data,
    AND the new "Price Trends" chart.
    """
    
    # 1. Get the specific area
    area = get_object_or_404(Area, pk=area_pk)
    
    # 2. Get all *ACTIVE* properties in this area
    properties_in_area = Property.objects.filter(
        area=area,
        status=PropertyStatus.ACTIVE
    ).order_by('-created_at')
    
    # 3. Get all amenities and group them by type (for the list)
    all_amenities = area.amenities.all().order_by('amenity_type', 'name')
    amenities_by_type = {}
    
    # 4. Create a JSON list of amenities *for the map*
    amenities_for_map = []
    
    for amenity in all_amenities:
        type_name = amenity.get_amenity_type_display()
        if type_name not in amenities_by_type:
            amenities_by_type[type_name] = []
        amenities_by_type[type_name].append(amenity)
        
        if amenity.latitude and amenity.longitude:
            map_details = amenity.get_map_details()
            amenities_for_map.append({
                'name': amenity.name,
                'type': amenity.get_amenity_type_display(),
                'lat': float(amenity.latitude),
                'lng': float(amenity.longitude),
                'icon': map_details['icon'],
                'color': map_details['color']
            })
            
    # --- 5. START: "PRICE TRENDS" LOGIC ---
    
    one_year_ago = timezone.now() - datetime.timedelta(days=365)
    
    sold_properties = Property.objects.filter(
        area=area,
        status=PropertyStatus.SOLD,
        sold_date__gte=one_year_ago
    )
    
    price_data = sold_properties.annotate(
        month=TruncMonth('sold_date')
    ).values(
        'month'
    ).annotate(
        avg_price=Avg('price')
    ).order_by('month')
    
    # --- 6. START: THIS IS THE FIX ---
    
    price_chart_labels = []
    price_chart_data = []
    
    # We MUST have at least 2 data points (months) to draw a line graph
    if price_data.count() > 1:
        for item in price_data:
            price_chart_labels.append(item['month'].strftime('%b %Y'))
            # We must convert the Decimal to a float for json.dumps
            price_chart_data.append(float(item['avg_price']))

    # --- END OF FIX ---
        
    # --- 7. Build the final context ---
    context = {
        'area': area,
        'properties': properties_in_area,
        'amenities_by_type': amenities_by_type,
        'amenities_json': json.dumps(amenities_for_map),
        
        # We now send the lists (which will be empty if data < 2)
        'price_chart_labels': json.dumps(price_chart_labels),
        'price_chart_data': json.dumps(price_chart_data),
    }
    
    return render(request, 'locations/area_detail.html', context)

def ajax_load_areas(request):
    """
    An "API" view that returns a list of areas for a given city_id.
    """
    city_id = request.GET.get('city_id')
    if city_id:
        areas = Area.objects.filter(city_id=city_id).order_by('name')
        data = [{'id': area.id, 'name': area.name} for area in areas]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)