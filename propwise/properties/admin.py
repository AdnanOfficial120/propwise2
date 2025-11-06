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
    
    list_display = (
        'title', 
        'area', 
        'is_verified', 
        'is_featured',  # <-- 1. ADD THIS
        'property_type', 
        'purpose', 
        'price', 
        'agent',
    )
    
    list_filter = (
        'is_verified', 
        'is_featured',  # <-- 2. ADD THIS
        'property_type', 
        'purpose', 
        'area__city'
    )
    
    search_fields = ('title', 'description', 'area__name', 'area__city__name')
    
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
        ('Admin Verification', {
            'fields': ('is_verified',)
        }),
        
        # --- 3. ADD THIS NEW SECTION FOR MONETIZATION ---
        ('Monetization (Admin Only)', {
            'classes': ('collapse',), # Makes this section collapsible
            'description': 'Check "Is Featured" and set an expiration date to feature this property.',
            'fields': ('is_featured', 'featured_until')
        }),
        # --- END OF NEW SECTION ---
    )

# Register your models here.
admin.site.register(Property, PropertyAdmin)
admin.site.register(PropertyImage)