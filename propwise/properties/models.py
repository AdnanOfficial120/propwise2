# properties/models.py

from django.db import models
from django.conf import settings # To get the User model
from locations.models import Area # To link to our Area model

# These are helper functions for our choices
class PropertyPurpose(models.TextChoices):
    FOR_SALE = 'sale', 'For Sale'
    FOR_RENT = 'rent', 'For Rent'

class PropertyType(models.TextChoices):
    HOUSE = 'house', 'House'
    PLOT = 'plot', 'Plot'
    APARTMENT = 'apartment', 'Apartment'
    COMMERCIAL = 'commercial', 'Commercial'
    OTHER = 'other', 'Other'

class AreaUnit(models.TextChoices):
    MARLA = 'marla', 'Marla'
    KANAL = 'kanal', 'Kanal'
    SQ_FT = 'sq_ft', 'Square Feet'
    SQ_YARD = 'sq_yard', 'Square Yards'


# properties/models.py



class Property(models.Model):
    """
    The main model for a property listing.
    """
    
    # Core Details
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.BigIntegerField()
    
    # --- UPGRADED LOCATION SECTION ---
    area = models.ForeignKey(
        Area, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="properties"
    )

    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Exact latitude of the property (e.g., 31.470510)"
    )
    
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True,
        help_text="Exact longitude of the property (e.g., 74.394170)"
    )
    
    # Choices
    purpose = models.CharField(max_length=10, choices=PropertyPurpose.choices)
    property_type = models.CharField(max_length=20, choices=PropertyType.choices)
    
    # Specs (supports our comparison tool)
    bedrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    bathrooms = models.PositiveSmallIntegerField(null=True, blank=True)
    area_size = models.DecimalField(max_digits=10, decimal_places=2)
    area_unit = models.CharField(max_length=10, choices=AreaUnit.choices, default=AreaUnit.MARLA)

    # Agent & Timestamps
    agent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="properties")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Main "Cover" Image
    main_image = models.ImageField(upload_to='properties/main_images/', null=True, blank=True)

    # --- TRUST & MONETIZATION FIELDS ---
    is_verified = models.BooleanField(
        default=False,
        help_text="Mark this listing as verified by the admin (e.g., checked for accuracy)."
    )
    
    # --- ADD THESE TWO NEW FIELDS for Monetization ---
    is_featured = models.BooleanField(
        default=False,
        help_text="Mark this listing as 'Featured' to show it at the top."
    )
    featured_until = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When this listing should stop being featured (e.g., 7 days from now)."
    )
    # --- END OF NEW FIELDS ---
    
    def __str__(self):
        return f"{self.title} in {self.area}"

class PropertyImage(models.Model): 
    """
    A model to store the image gallery for a property.
    """
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='properties/gallery/')
    
    def __str__(self):
        return f"Image for {self.property.title}"