# locations/admin.py

from django.contrib import admin
from .models import City, Area, Amenity  # <-- 1. IMPORT THE NEW 'Amenity' MODEL

# Register your models here.

# We will keep the City admin simple
admin.site.register(City)


# --- 2. CREATE A NEW "INLINE" CLASS FOR AMENITIES ---
class AmenityInline(admin.TabularInline):
    """
    This allows us to add/edit Amenities directly from the Area admin page.
    'TabularInline' makes it look like a clean table.
    """
    model = Amenity
    # These are the fields that will show up in the table
    fields = ('name', 'amenity_type', 'latitude', 'longitude')
    
    # This just adds one empty "extra" row at the bottom
    extra = 1 
    
    # This makes the whole section collapsible
    classes = ('collapse',) 


# --- 3. UPGRADE THE 'AreaAdmin' CLASS ---
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    """
    Custom admin options for the Area model.
    """
    
    list_display = (
        'name', 
        'city', 
        'latitude', 
        'longitude',
    )
    list_filter = ('city',)
    search_fields = ('name', 'city__name')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'city')
        }),
        ('Neighborhood Insights (Optional)', {
            'classes': ('collapse',),
            'description': 'Add the area description and map coordinates here.',
            'fields': (
                'description', 
                'latitude', 
                'longitude'
            ),
        }),
    )
    
    # --- THIS IS THE NEW LINE THAT CONNECTS EVERYTHING ---
    # It tells the Area admin to show the AmenityInline table
    inlines = [AmenityInline]