# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from properties.models import Property
# accounts/models.py this is for notification on saved search

from django.utils import timezone
from locations.models import City
from properties.models import PropertyType, PropertyPurpose

class User(AbstractUser):
   
    
    # We will use the default `username`, `email`, `first_name`, `last_name`
    # from AbstractUser.

    # Our custom fields to distinguish user types
    is_agent = models.BooleanField('Is agent', default=False)
    is_buyer = models.BooleanField('Is buyer', default=True) # By default, users are buyers
    
    # Other profile fields
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    # --- ADD THIS NEW FIELD  for as add to fovorites---
    favorites = models.ManyToManyField(
        Property, 
        related_name="favorited_by", 
        blank=True
    )

    def __str__(self):
        return self.username
    





    # accounts/models.py for notification 

class SavedSearch(models.Model):
    """
    Stores a user's saved search criteria.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="saved_searches")
    name = models.CharField(max_length=100) # e.g., "My Future Home"

    # --- Fields to store the filter values ---
    keyword = models.CharField(max_length=255, null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    property_type = models.CharField(max_length=50, choices=PropertyType.choices, null=True, blank=True)
    purpose = models.CharField(max_length=50, choices=PropertyPurpose.choices, null=True, blank=True)
    
    # For RangeFilters like 'price' and 'bedrooms'
    min_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    max_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    min_bedrooms = models.PositiveIntegerField(null=True, blank=True)
    
    # --- Fields for the alert system ---
    is_active = models.BooleanField(default=True, help_text="Is this alert active?")
    last_checked = models.DateTimeField(default=timezone.now, help_text="When the alert was last run.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    class Meta:
        # A user can't have two saved searches with the same name
        unique_together = ('user', 'name')