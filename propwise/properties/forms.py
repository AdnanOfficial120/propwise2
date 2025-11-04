# properties/forms.py

from django import forms
from .models import Property, PropertyImage
from locations.models import City, Area

class PropertyForm(forms.ModelForm):
    """
    A form for creating and updating Property listings.
    Now includes a cascading dropdown for City -> Area.
    """
    
    gallery_images = forms.FileField(
        label="Gallery Images",
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
        })
    )

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
            'area': forms.Select(attrs={'class': 'form-select', 'id': 'id_area'}),
            'purpose': forms.Select(attrs={'class': 'form-select'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'area_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'area_unit': forms.Select(attrs={'class': 'form-select'}),
            'main_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    # --- THIS IS THE UPDATED __init__ METHOD ---
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # This must be called first

        # --- Add the City field ---
        self.fields['city'] = forms.ModelChoiceField(
            queryset=City.objects.all().order_by('name'),
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_city'}),
            required=False, # City is not required by the *model*, only by the form logic
            label="City"
        )

        # --- New Cascading Logic ---
        
        if self.instance and self.instance.pk and self.instance.area:
            # --- A. EDIT MODE (Existing Property) ---
            # This is an "Edit" form. Pre-fill both fields.
            city = self.instance.area.city
            self.fields['city'].initial = city
            self.fields['area'].queryset = Area.objects.filter(city=city).order_by('name')
        
        elif self.is_bound:
            # --- B. SUBMIT MODE (POST Request) ---
            # This is a "New" form that is being submitted.
            # We MUST populate the area queryset *before* validation.
            try:
                # Get the submitted city_id from the POST data
                city_id = self.data.get('city')
                if city_id:
                    self.fields['area'].queryset = Area.objects.filter(city_id=city_id).order_by('name')
                else:
                    self.fields['area'].queryset = Area.objects.none()
            except (ValueError, TypeError):
                self.fields['area'].queryset = Area.objects.none() # Safety fallback
        
        else:
            # --- C. NEW MODE (GET Request) ---
            # This is a new, blank form being loaded for the first time.
            # The 'area' dropdown should be empty.
            self.fields['area'].queryset = Area.objects.none()


        # --- Re-order the fields ---
        field_order = list(self.Meta.fields)
        area_index = field_order.index('area')
        field_order.insert(area_index, 'city')
        self.order_fields(field_order)

        # --- Original logic ---
        self.fields['bedrooms'].required = False
        self.fields['bathrooms'].required = False
        if self.instance and self.instance.pk and self.instance.main_image:
            self.fields['main_image'].required = False