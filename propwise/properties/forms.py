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
            'latitude',
            'longitude',
            'purpose', 
            'property_type', 
            'bedrooms', 
            'bathrooms', 
            'area_size', 
            'area_unit',
            'main_image',
            'video_url', # <-- 1. ADD 'video_url' TO THIS LIST
        ]
        
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'area': forms.Select(attrs={'class': 'form-select', 'id': 'id_area'}),
            'latitude': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 28.3588'
            }),
            'longitude': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., 70.3009'
            }),
            'purpose': forms.Select(attrs={'class': 'form-select'}),
            'property_type': forms.Select(attrs={'class': 'form-select'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'area_size': forms.NumberInput(attrs={'class': 'form-control'}),
            'area_unit': forms.Select(attrs={'class': 'form-select'}),
            'main_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            
            # --- 2. ADD WIDGET FOR 'video_url' ---
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.youtube.com/watch?v=...'
            }),
            # --- END OF NEW WIDGET ---
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) # This must be called first

        self.fields['city'] = forms.ModelChoiceField(
            queryset=City.objects.all().order_by('name'),
            widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_city'}),
            required=False, 
            label="City"
        )
        
        self.fields['latitude'].help_text = "Go to Google Maps, right-click the property, and click the coordinates to copy."
        self.fields['longitude'].help_text = "This is the second coordinate number from Google Maps."
        
        # --- ADD HELP TEXT FOR 'video_url' ---
        self.fields['video_url'].help_text = "Optional. Paste a link to a YouTube or Vimeo video."

        # --- New Cascading Logic ---
        if self.instance and self.instance.pk and self.instance.area:
            city = self.instance.area.city
            self.fields['city'].initial = city
            self.fields['area'].queryset = Area.objects.filter(city=city).order_by('name')
        
        elif self.is_bound:
            try:
                city_id = self.data.get('city')
                if city_id:
                    self.fields['area'].queryset = Area.objects.filter(city_id=city_id).order_by('name')
                else:
                    self.fields['area'].queryset = Area.objects.none()
            except (ValueError, TypeError):
                self.fields['area'].queryset = Area.objects.none() 
        
        else:
            self.fields['area'].queryset = Area.objects.none()

        # --- Re-order the fields ---
        field_order = list(self.Meta.fields)
        area_index = field_order.index('area')
        field_order.insert(area_index, 'city')
        field_order.insert(area_index + 1, 'latitude')
        field_order.insert(area_index + 2, 'longitude')
        
        # --- 3. ADD 'video_url' TO THE FIELD ORDER ---
        main_image_index = field_order.index('main_image')
        field_order.insert(main_image_index + 1, 'video_url')
        # --- END OF NEW ORDER ---
        
        self.order_fields(field_order)

        # --- Original logic ---
        self.fields['bedrooms'].required = False
        self.fields['bathrooms'].required = False
        if self.instance and self.instance.pk and self.instance.main_image:
            self.fields['main_image'].required = False