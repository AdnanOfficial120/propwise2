# locations/models.py

from django.db import models
from django.conf import settings # <-- 1. ADD THIS IMPORT FOR THE USER MODEL

class City(models.Model):
    """
    Model to store city names, e.g., 'Lahore', 'Karachi'.
    """
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = "Cities" # Fixes "Citys" in the admin panel

    def __str__(self):
        return self.name

class Area(models.Model):
    """
    Model to store specific areas/neighborhoods within a city.
    e.g., 'DHA Phase 6', 'Gulberg 3'
    """
    name = models.CharField(max_length=150)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="areas")
    
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

    class Meta:
        # Ensures that one city cannot have two areas with the same name
        unique_together = ('name', 'city')
    
    def __str__(self):
        return f"{self.name}, {self.city.name}"
    
    # --- NOTE: I removed the duplicate Meta and __str__ from your file ---


class AmenityType(models.TextChoices):
    """
    Defines the "types" of amenities we want to track.
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
        on_delete=models.CASCADE,
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
        verbose_name_plural = "Amenities"
        ordering = ['amenity_type', 'name'] # Group by type, then name

    def __str__(self):
        return f"{self.name} ({self.get_amenity_type_display()}) in {self.area.name}"
    
    # --- NOTE: I MOVED THIS FUNCTION *INSIDE* THE AMENITY CLASS ---
    def get_map_details(self):
        """
        This helper function returns the correct color and
        Font Awesome icon name for each amenity type.
        """
        if self.amenity_type == AmenityType.SCHOOL:
            return {'icon': 'school', 'color': 'blue'}
        elif self.amenity_type == AmenityType.HOSPITAL:
            return {'icon': 'hospital-o', 'color': 'red'}
        elif self.amenity_type == AmenityType.PARK:
            return {'icon': 'tree', 'color': 'green'}
        elif self.amenity_type == AmenityType.RESTAURANT:
            return {'icon': 'cutlery', 'color': 'orange'}
        elif self.amenity_type == AmenityType.SUPERMARKET:
            return {'icon': 'shopping-cart', 'color': 'purple'}
        else:
            return {'icon': 'info-circle', 'color': 'gray'}
    # --- END OF FUNCTION ---


# --- START: NEW "COMMUNITY Q&A" MODELS ---

class Question(models.Model):
    """
    A user-submitted question about a specific Area.
    """
    area = models.ForeignKey(
        Area, 
        on_delete=models.CASCADE, 
        related_name="questions"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Keep question even if user is deleted
        null=True
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at'] # Newest questions first

    def __str__(self):
        return f"Q: {self.title} (in {self.area.name})"


class Answer(models.Model):
    """
    An answer to a user-submitted question.
    Can be written by any user (buyer or agent).
    """
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name="answers"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Keep answer even if user is deleted
        null=True
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # Oldest (first) answers first

    def __str__(self):
        return f"A: {self.body[:50]}... (for Q: {self.question.title[:20]}...)"

# --- END: NEW "COMMUNITY Q&A" MODELS ---