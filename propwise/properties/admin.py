# properties/admin.py

from django.contrib import admin
from .models import Property, PropertyImage

class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 3 

class PropertyAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for the Property model.
    """
    inlines = [PropertyImageInline]
    
    # --- ADD LAT/LNG TO THE LIST DISPLAY ---
    list_display = (
        'title', 
        'area', 
        'property_type', 
        'purpose', 
        'price', 
        'agent',
        'latitude',
        'longitude'
    )
    
    list_filter = ('property_type', 'purpose', 'area__city')
    search_fields = ('title', 'description', 'area__name', 'area__city__name')
    
    # --- ADD FIELDSETS TO ORGANIZE THE EDIT PAGE ---
    fieldsets = (
        ('Core Information', {
            'fields': ('title', 'description', 'price', 'agent')
        }),
        ('Location', {
            'fields': ('area', 'latitude', 'longitude')
        }),
        ('Property Details', {
            'fields': ('purpose', 'property_type', 'bedrooms', 'bathrooms', 'area_size', 'area_unit')
        }),
        ('Images', {
            'fields': ('main_image',)
        }),
    )

# Register your models here.
admin.site.register(Property, PropertyAdmin)
admin.site.register(PropertyImage)