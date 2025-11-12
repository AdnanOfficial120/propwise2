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
        'is_featured',
        'status',
        'property_type', 
        'purpose', 
        'price', 
        'agent',
    )
    
    list_filter = (
        'is_verified', 
        'is_featured',
        'status',
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
        
        # --- ADD 'video_url' TO THIS SECTION ---
        ('Images & Video', {
            'fields': ('main_image', 'video_url')
        }),
        # --- END OF CHANGE --- 
        # --- 3. ADD 'status' AND 'sold_date' TO THIS SECTION ---
        ('Admin Status Control', {
            'classes': ('collapse',),
            'fields': ('is_verified', 'is_featured', 'featured_until', 'status', 'sold_date')
        }),
    )
    
    # We remove the old "Admin Verification" and "Monetization" sections
    # and combine them into the single "Admin Status Control" section above.

# Register your models here.
admin.site.register(Property, PropertyAdmin)
admin.site.register(PropertyImage)