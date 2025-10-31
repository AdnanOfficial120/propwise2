# properties/filters.py (NEW FILE)

import django_filters
from django_filters import CharFilter, ModelChoiceFilter, ChoiceFilter, RangeFilter
from .models import Property, PropertyType, PropertyPurpose
from locations.models import City

class PropertyFilter(django_filters.FilterSet):
    """
    This class defines the filters we want to apply to the Property model.
    """
    
    # Filter 1: Keyword search on 'title' and 'description'
    # 'icontains' means "case-insensitive contains"
    keyword = CharFilter(field_name='title', lookup_expr='icontains', label='Keyword')
    
    # Filter 2: Dropdown for City
    # We filter on 'area__city' (a related field)
    city = ModelChoiceFilter(
        field_name='area__city',
        queryset=City.objects.all(),
        label='City'
    )
    
    # Filter 3: Dropdown for Property Type
    property_type = ChoiceFilter(
        choices=PropertyType.choices,
        label='Property Type'
    )
    
    # Filter 4: Dropdown for Purpose
    purpose = ChoiceFilter(
        choices=PropertyPurpose.choices,
        label='Purpose'
    )
    
    # Filter 5: Min/Max Price Range
    # This will automatically create two fields: 'price_min' and 'price_max'
    price = RangeFilter(label='Price Range')
    # --- ADD THIS NEW FILTER ---
    bedrooms = RangeFilter(label='Bedrooms (e.g., Min/Max)')

    class Meta:
        model = Property
        # These are the fields we are filtering *against*.
        # The filters we defined above will be *used* to filter these fields.
        fields = ['keyword', 'city', 'property_type', 'purpose', 'price', 'bedrooms']