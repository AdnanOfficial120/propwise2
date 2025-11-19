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

# This is the TextChoice class for the "Sold Data" module
class PropertyStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    SOLD = 'sold', 'Sold'
    EXPIRED = 'expired', 'Expired'


# This is the main Property model
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
    
    # Specs
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
    is_featured = models.BooleanField(
        default=False,
        help_text="Mark this listing as 'Featured' to show it at the top."
    )
    featured_until = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When this listing should stop being featured (e.g., 7 days from now)."
    )
    status = models.CharField(
        max_length=10,
        choices=PropertyStatus.choices,
        default=PropertyStatus.ACTIVE,
        help_text="The current status of the listing (e.g., Active, Sold)."
    )
    sold_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="The date and time this property was marked as sold."
    )
    
    # --- FIELD FOR VIDEO TOUR ---
    video_url = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        help_text="A link to a YouTube or Vimeo video walkthrough (e.g., https://www.youtube.com/watch?v=...)"
    )
    
    def __str__(self):
        return f"{self.title} in {self.area}"

    # --- THIS IS YOUR NEW VIDEO HELPER FUNCTION ---
    # properties/models.py (inside your Property class)

    def get_video_embed_url(self):
        """
        This function converts a standard YouTube or Vimeo URL
        into the correct URL format needed for embedding in an <iframe>.
        
        NOW UPGRADED to also handle YouTube "Shorts" links.
        """
        if not self.video_url:
            return None
        
        url = self.video_url
        video_id = None

        # Handle standard YouTube links
        if "youtube.com/watch?v=" in url:
            video_id = url.split('v=')[-1].split('&')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        
        # Handle short YouTube links
        if "youtu.be/" in url:
            video_id = url.split('/')[-1].split('?')[0]
            return f"https://www.youtube.com/embed/{video_id}"

        # --- THIS IS THE NEW FIX ---
        # Handle new YouTube "Shorts" links
        if "youtube.com/shorts/" in url:
            video_id = url.split('/shorts/')[-1].split('?')[0]
            return f"https://www.youtube.com/embed/{video_id}"
        # --- END OF NEW FIX ---

        # Handle Vimeo links
        if "vimeo.com/" in url:
            video_id = url.split('/')[-1].split('?')[0]
            return f"https://player.vimeo.com/video/{video_id}"
        
        # If it's not a recognized service, we can't embed it
        return None
# This is your PropertyImage model, now correctly indented
class PropertyImage(models.Model): 
    """
    A model to store the image gallery for a property.
    """
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='properties/gallery/')
    
    def __str__(self):
        return f"Image for {self.property.title}"

        # agent dashboard analsisis

class PropertyView(models.Model):
    """
    Tracks a single 'view' on a property detail page.
    Used for Agent Analytics.
    """
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name="views"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Optional: If the viewer was logged in, track who they were
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )

    class Meta:
        # Most recent views first
        ordering = ['-timestamp']

    def __str__(self):
        return f"View on {self.property.title} at {self.timestamp}"