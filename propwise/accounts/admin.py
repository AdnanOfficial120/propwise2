# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SavedSearch, AgentRating, Lead, Notification

# 1. Register the Custom User Model
# We use the built-in UserAdmin for a professional look
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # Add our custom fields to the list view
    list_display = ('username', 'email', 'is_agent', 'is_buyer', 'is_staff')
    # Add filters
    list_filter = ('is_agent', 'is_buyer', 'is_staff', 'is_superuser')
    
    # Add our custom fields to the "Edit User" page
    fieldsets = UserAdmin.fieldsets + (
        ('PropWise Profile', {'fields': ('is_agent', 'is_buyer', 'phone_number', 'profile_picture')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('PropWise Profile', {'fields': ('is_agent', 'is_buyer', 'phone_number', 'profile_picture')}),
    )

# 2. Register Saved Search
@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'city', 'created_at')
    list_filter = ('city',)

# 3. Register Agent Ratings
@admin.register(AgentRating)
class AgentRatingAdmin(admin.ModelAdmin):
    list_display = ('agent', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')

# 4. Register Leads (The CRM)
@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('contact_name', 'status', 'agent', 'source', 'created_at')
    list_filter = ('status', 'source')

# 5. Register Notifications (The Bell Icon) -- THIS IS THE MISSING ONE
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')