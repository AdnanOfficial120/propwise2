# accounts/forms.py
from django.contrib.auth.forms import UserCreationForm
# We can remove UserChangeForm, we don't need it
from django import forms  # <-- Make sure this is imported
from django.contrib.auth import get_user_model
# accounts/forms.py notification to show 
from .models import SavedSearch,AgentRating,Lead
from properties.models import Property, PropertyStatus
#for visitschedule
from .models import VisitRequest

# This gets your custom user model (accounts.User)
User = get_user_model()


# --- YOUR CustomUserCreationForm STAYS THE SAME ---
class CustomUserCreationForm(UserCreationForm):
    """
    A form for creating new users. Includes all required
    fields, plus our custom fields.
    """
    
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'is_agent')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_agent'].label = "I am signing up as an Agent/Agency"


# --- REPLACE YOUR OLD CustomUserChangeForm WITH THIS ---

class CustomUserChangeForm(forms.ModelForm): # <-- 1. Inherit from ModelForm
    """
    A form for users to update their public profile information.
    """
    class Meta:
        model = User
        # 2. Update the fields list
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'profile_picture']
        
        # 3. Add widgets to make it look good
     
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # accounts/forms.py for notificanton o fsaved

class SavedSearchForm(forms.ModelForm):
    """
    A simple form for creating or updating a SavedSearch.
    The user only needs to provide a name.
    """
    class Meta:
        model = SavedSearch
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., "My Future Home" or "Islamabad Apartments"'
            }),
        }
        labels = {
            'name': 'Save Search As:'
        }
# accounts/forms.py 
# --- ADD THIS NEW FORM FOR AGENT RATINGS ---

class AgentRatingForm(forms.ModelForm):
    """
    A form for a user to submit a rating and review for an agent.
    """
    class Meta:
        model = AgentRating
        
        # We only want the user to fill out these two fields
        fields = ['rating', 'comment']
        
        widgets = {
            'rating': forms.Select(
                attrs={
                    'class': 'form-select', 
                }
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control', 
                    'rows': 4,
                    'placeholder': 'Share your experience with this agent...'
                }
            ),
        }
        
        labels = {
            'rating': 'Your Rating (1-5 Stars)',
            'comment': 'Your Review',
        }

    def __init__(self, *args, **kwargs):
        """
        Make the comment field optional.
        """
        super().__init__(*args, **kwargs)
        self.fields['comment'].required = False




  

# --- ADD THIS NEW FORM FOR THE "LEAD MANAGER" ---

class LeadForm(forms.ModelForm):
    """
    A form for an agent to manually create or update a Lead.
    """
    class Meta:
        model = Lead
        # These are the fields the agent will fill out.
        # The 'agent' field is set automatically in the view.
        fields = [
            'contact_name', 
            'contact_email', 
            'contact_phone', 
            'status', 
            'source', 
            'property_of_interest', 
            'notes'
        ]
        
        widgets = {
            'contact_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g., Ali Khan'
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g., ali@example.com'
            }),
            'contact_phone': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g., 0300-1234567'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'source': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g., Phone Call, Walk-in'
            }),
            'property_of_interest': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'placeholder': 'Private notes about this lead...'
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        This is the "magic" part. We pass in the 'user' (agent)
        to filter the 'property_of_interest' dropdown.
        """
        # Get the agent (user) from the arguments
        agent = kwargs.pop('agent', None) 
        
        super().__init__(*args, **kwargs)
        
        # Make these fields optional
        self.fields['contact_email'].required = False
        self.fields['contact_phone'].required = False
        self.fields['source'].required = False
        self.fields['property_of_interest'].required = False
        self.fields['notes'].required = False

        if agent:
            # THIS IS THE KEY:
            # Filter the 'property_of_interest' queryset to only show
            # this agent's own *active* properties.
            self.fields['property_of_interest'].queryset = Property.objects.filter(
                agent=agent,
                status=PropertyStatus.ACTIVE
            ).order_by('-created_at')    

# this is fot visting scheduled

class VisitRequestForm(forms.ModelForm):
    class Meta:
        model = VisitRequest
        fields = ['visit_date', 'message']
        
        widgets = {
            'visit_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local' # This creates the HTML5 date/time picker
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g., I am available after 5 PM...'
            }),
        }
        labels = {
            'visit_date': 'Preferred Date & Time',
            'message': 'Message (Optional)',
        }