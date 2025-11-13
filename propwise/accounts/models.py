# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser
from properties.models import Property
# accounts/models.py this is for notification on saved search

from django.utils import timezone
from locations.models import City
from properties.models import PropertyType, PropertyPurpose
# accounts/models.py This is a tool from Django that will help us ensure the rating field must be a number between 1 and 5.

from django.core.validators import MinValueValidator, MaxValueValidator

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




# accounts/models.py  for rating system
class AgentRating(models.Model):
    """
    Stores a single rating and review given by a user to an agent.
    """
    # --- Choices for the 5-star rating ---
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )

    agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="ratings_received",
        limit_choices_to={'is_agent': True}, # Ensures this MUST be an agent
        help_text="The agent being rated."
    )
    
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL, # If reviewer is deleted, keep the review
        null=True,
        related_name="ratings_given",
        help_text="The user who wrote the review."
    )
    
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 (Poor) to 5 (Excellent)."
    )
    
    comment = models.TextField(
        blank=True,
        null=True,
        help_text="The text review/comment."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # A user can only rate an agent one time
        unique_together = ('agent', 'reviewer')
        # By default, show the newest reviews first
        ordering = ['-created_at']

    def __str__(self):
        # This is what will show up in the Django Admin
        return f"{self.reviewer.username} rated {self.agent.username}: {self.rating} stars"
    





   

# --- TWO CLASSES FOR THE "LEAD MANAGER" MODULE ---

class LeadStatus(models.TextChoices):
    """
    Defines the sales pipeline steps for an agent.
    """
    NEW = 'new', 'New'
    CONTACTED = 'contacted', 'Contacted'
    FOLLOW_UP = 'follow_up', 'Follow-up'
    VISIT_SCHEDULED = 'visit_scheduled', 'Visit Scheduled'
    NOT_INTERESTED = 'not_interested', 'Not Interested'
    CLOSED = 'closed', 'Closed'

class Lead(models.Model):
    """
    This is the "digital notebook" for an agent.
    It stores a single lead (a potential customer).
    """
    agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # If agent is deleted, their leads are deleted
        related_name="leads",
        limit_choices_to={'is_agent': True}, # Ensures this MUST be an agent
        help_text="The agent this lead belongs to."
    )
    
    # --- Lead's Contact Info ---
    contact_name = models.CharField(
        max_length=255, 
        help_text="The lead's full name (e.g., Ali Khan)"
    )
    contact_email = models.EmailField(
        max_length=255, 
        blank=True, 
        null=True
    )
    contact_phone = models.CharField(
        max_length=20, 
        blank=True, 
        null=True
    )
    
    # --- Lead's Status ---
    status = models.CharField(
        max_length=20,
        choices=LeadStatus.choices,
        default=LeadStatus.NEW,
        help_text="The current stage of this lead in the sales pipeline."
    )
    
    source = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Where this lead came from (e.g., 'PropWise Chat', 'Phone Call')"
    )
    
    # --- Optional: Link to the property they were interested in ---
    property_of_interest = models.ForeignKey(
        Property,
        on_delete=models.SET_NULL, # If property is deleted, keep the lead
        null=True,
        blank=True,
        related_name="leads"
    )
    
    # --- Agent's Private Notes ---
    notes = models.TextField(
        blank=True, 
        null=True,
        help_text="Agent's private notes about this lead."
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Show the newest leads first
        ordering = ['-created_at']

    def __str__(self):
        return f"Lead for {self.agent.username}: {self.contact_name}"