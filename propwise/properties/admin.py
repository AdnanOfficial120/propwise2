# properties/admin.py

from django.contrib import admin
from .models import Property, PropertyImage

class PropertyImageInline(admin.TabularInline):
    """
    This allows us to add/edit PropertyImage objects
    directly from the Property admin page.
    """
    model = PropertyImage
    extra = 3  # How many extra "empty" image slots to show

class PropertyAdmin(admin.ModelAdmin):
    """
    Customizes the admin interface for the Property model.
    """
    inlines = [PropertyImageInline]
    list_display = ('title', 'area', 'property_type', 'purpose', 'price', 'agent')
    list_filter = ('property_type', 'purpose', 'area__city')
    search_fields = ('title', 'description', 'area__name', 'area__city__name')

# Register your models here.
admin.site.register(Property, PropertyAdmin)
admin.site.register(PropertyImage) # We register this just in case