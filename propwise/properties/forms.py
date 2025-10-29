from django import forms
from .models import Property, PropertyImage

class PropertyForm(forms.ModelForm):
    """
    A form for creating and updating Property listings.
    """
    
    # --- THIS IS THE CORRECTED FIELD ---
    # We remove 'multiple': True from the widget attrs to stop the ValueError
    gallery_images = forms.FileField(
        label="Gallery Images",
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            # 'multiple': True has been REMOVED from here.
        })
    )
    # --- END OF CORRECTION ---

    class Meta:
        model = Property
        fields = [
            'title', 
            'description', 
            'price', 
            'area', 
            'purpose', 
            'property_type', 
            'bedrooms', 
            'bathrooms', 
            'area_size', 
            'area_unit',
            'main_image'
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'area': forms.Select(attrs={'class': 'form-select'}),
            'purpose': forms.Select(attrs={'class': 'form-select'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'area_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'area_unit': forms.Select(attrs={'class': 'form-select'}),
            'main_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

   # In properties/forms.py, inside the PropertyForm class

def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    
    self.fields['bedrooms'].required = False
    self.fields['bathrooms'].required = False

    # --- THIS WAS THE FIX ---
    if self.instance and self.instance.pk and self.instance.main_image:
        self.fields['main_image'].required = False
    # --- END OF FIX ---