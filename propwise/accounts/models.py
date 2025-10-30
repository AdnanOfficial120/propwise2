# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from properties.models import Property

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