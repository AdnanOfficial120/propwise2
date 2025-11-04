# locations/admin.py

from django.contrib import admin
from .models import City, Area

# Register your models here.

# We will keep the City admin simple
admin.site.register(City)


# --- Create a custom admin class for Area ---
@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    """
    Custom admin options for the Area model.
    """
    
    # 1. This controls the columns you see in the list of all areas
    list_display = (
        'name', 
        'city', 
        'latitude', 
        'longitude',
    )
    
    # 2. This filters the list by city
    list_filter = ('city',)
    
    # 3. This allows you to search by name or city name
    search_fields = ('name', 'city__name')
    
    # 4. This is the most important part:
    # It organizes the "Edit" page for an area into logical sections.
    fieldsets = (
        (None, {  # 'None' means the first section has no title
            'fields': ('name', 'city')
        }),
        ('Neighborhood Insights (Optional)', {
            'classes': ('collapse',),  # Makes this section collapsible
            'description': 'Add the area description and map coordinates here.',
            'fields': (
                'description', 
                'latitude', 
                'longitude'
            ),
        }),
    )

# Note: We remove the old 'admin.site.register(Area)' because
# the '@admin.register(Area)' decorator does the same job.