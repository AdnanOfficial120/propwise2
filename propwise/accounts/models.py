# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Custom User Model for PropWise.
    
    We inherit from AbstractUser to get all of Django's built-in
    authentication features (password handling, groups, permissions, etc.).
    
    We can add our own custom fields here.
    """
    
    # We will use the default `username`, `email`, `first_name`, `last_name`
    # from AbstractUser.

    # Our custom fields to distinguish user types
    is_agent = models.BooleanField('Is agent', default=False)
    is_buyer = models.BooleanField('Is buyer', default=True) # By default, users are buyers
    
    # Other profile fields
    phone_number = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return self.username