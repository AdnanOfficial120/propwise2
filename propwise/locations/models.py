# locations/models.py

from django.db import models

class City(models.Model):
    """
    Model to store city names, e.g., 'Lahore', 'Karachi'.
    """
    name = models.CharField(max_length=100, unique=True)
    # We can add more fields later, like state/province.
    
    class Meta:
        verbose_name_plural = "Cities" # Fixes "Citys" in the admin panel

    def __str__(self):
        return self.name

# locations/models.py
# (Your City model stays the same, no changes needed)

class Area(models.Model):
    """
    Model to store specific areas/neighborhoods within a city.
    e.g., 'DHA Phase 6', 'Gulberg 3'
    """
    name = models.CharField(max_length=150)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="areas")
    
    # --- START OF NEIGHBORHOOD INSIGHTS FIELDS ---
    
    description = models.TextField(
        blank=True, 
        null=True,
        help_text="A detailed description of the neighborhood (e.g., amenities, lifestyle)."
    )

    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Latitude for the map (e.g., 31.470510)"
    )
    
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Longitude for the map (e.g., 74.394170)"
    )

    # --- END OF NEIGHBORHOOD INSIGHTS FIELDS ---

    class Meta:
        # Ensures that one city cannot have two areas with the same name
        unique_together = ('name', 'city')
    
    def __str__(self):
        return f"{self.name}, {self.city.name}"

    class Meta:
        # Ensures that one city cannot have two areas with the same name
        unique_together = ('name', 'city')
    
    def __str__(self):
        return f"{self.name}, {self.city.name}"
    


# locations/models.py Feature 1 (Hyper-Local)

# --- ADDed xTHESE TWO NEW CLASSES FOR THE "HYPER-LOCAL" MODULE ---

class AmenityType(models.TextChoices):
    """
    Defines the "types" of amenities we want to track.
    This lets us group them on the website.
    """
    SCHOOL = 'school', 'School'
    HOSPITAL = 'hospital', 'Hospital'
    PARK = 'park', 'Park'
    RESTAURANT = 'restaurant', 'Restaurant'
    SUPERMARKET = 'supermarket', 'Supermarket'
    OTHER = 'other', 'Other'


class Amenity(models.Model):
    """
    Stores a single "Point of Interest" or Amenity and
    links it to a specific Area.
    """
    area = models.ForeignKey(
        Area, 
        on_delete=models.CASCADE,  # If an Area is deleted, its amenities go with it
        related_name="amenities"
    )
    
    name = models.CharField(
        max_length=255,
        help_text="e.g., 'Beaconhouse School' or 'Green Valley Supermarket'"
    )
    
    amenity_type = models.CharField(
        max_length=20,
        choices=AmenityType.choices,
        default=AmenityType.OTHER
    )
    
    # We make these optional. This is a SMART design.
    # It allows you to quickly list "5 schools" without
    # needing to find all their map coordinates right away.
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Optional: Latitude for this amenity's map pin"
    )
    
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Optional: Longitude for this amenity's map pin"
    )

    class Meta:
        # This makes it look nice in the admin panel
        verbose_name_plural = "Amenities"
        ordering = ['amenity_type', 'name'] # Group by type, then name

    def __str__(self):
        return f"{self.name} ({self.get_amenity_type_display()}) in {self.area.name}"
    


#this is fo rshowing icon in mapppp
    def get_map_details(self):
        """
        This helper function returns the correct color and
        Font Awesome icon name for each amenity type.
        """
        if self.amenity_type == AmenityType.SCHOOL:
            return {'icon': 'school', 'color': 'blue'}
        
        elif self.amenity_type == AmenityType.HOSPITAL:
            return {'icon': 'hospital-o', 'color': 'red'} # 'hospital-o' is the "H" icon
        
        elif self.amenity_type == AmenityType.PARK:
            return {'icon': 'tree', 'color': 'green'}
            
        elif self.amenity_type == AmenityType.RESTAURANT:
            return {'icon': 'cutlery', 'color': 'orange'} # 'cutlery' is a knife/fork
            
        elif self.amenity_type == AmenityType.SUPERMARKET:
            return {'icon': 'shopping-cart', 'color': 'purple'}
            
        else:
            # Default for "Other"
            return {'icon': 'info-circle', 'color': 'gray'}
    # --- END OF NEW FUNCTION ---

    class Meta:
        # ... (your existing Meta class)
        verbose_name_plural = "Amenities"
        ordering = ['amenity_type', 'name']
    