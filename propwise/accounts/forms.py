# accounts/forms.py
from django.contrib.auth.forms import UserCreationForm
# We can remove UserChangeForm, we don't need it
from django import forms  # <-- Make sure this is imported
from django.contrib.auth import get_user_model

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
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }