
# properties/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Property, PropertyImage,PropertyStatus  # Make sure PropertyImage is imported
from .filters import PropertyFilter
from .forms import PropertyForm
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
# properties/views.py for notification of saved serches
from accounts.forms import SavedSearchForm
from django.db import IntegrityError
from decimal import Decimal
# properties/views.py (for map view)
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.humanize.templatetags.humanize import intcomma
from geopy.distance import geodesic
from locations.models import Amenity
#for Ai description extra
import os
import json
import google.generativeai as genai
from django.views.decorators.http import require_POST
from django.conf import settings # To get the User model
# properties/views.py (right after imports)
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
#these are for payment 7 day etc
from django.utils import timezone
from django.db.models import Case, When, BooleanField

# properties/views.py

# ---  'property_detail' with distance measure---

def property_detail(request, pk):
    # 1. Get the main property and gallery (same as before)
    property = get_object_or_404(Property, pk=pk)
    gallery_images = property.images.all()
    
    # --- 2. NEW: CALCULATE NEARBY AMENITIES ---
    
    nearby_amenities = [] # Start with an empty list

    # We can only calculate distance if the *property* has coordinates
    if property.latitude and property.longitude:
        
        # This is Point A (the property's location)
        prop_point = (property.latitude, property.longitude)
        
        # Get all amenities that *also* have coordinates
        all_amenities = Amenity.objects.filter(
            latitude__isnull=False, 
            longitude__isnull=False
        )
        
        amenities_with_distance = []
        
        # Loop through every amenity to find its distance
        for amenity in all_amenities:
            
            # This is Point B (the amenity's location)
            amenity_point = (amenity.latitude, amenity.longitude)
            
            # Use geopy to calculate the distance
            distance_km = geodesic(prop_point, amenity_point).km
            
            # Add the amenity and its distance to our list
            amenities_with_distance.append({
                'amenity': amenity,
                'distance': distance_km
            })
        
        # Sort the list by distance, from closest to farthest
        sorted_amenities = sorted(amenities_with_distance, key=lambda x: x['distance'])
        
        # Get just the Top 5 closest amenities
        nearby_amenities = sorted_amenities[:5]

    # --- 3. BUILD THE FINAL CONTEXT ---
    context = {
        'property': property,
        'gallery_images': gallery_images,
        'nearby_amenities': nearby_amenities, # <-- Add our new list to the context
    }
    
    return render(request, 'properties/property_detail.html', context)

# properties/views.py

# --- REPLACE YOUR OLD 'property_search' FUNCTION WITH THIS ---

# properties/views.py

# --- REPLACE YOUR 'property_search' FUNCTION WITH THIS ---

# properties/views.py

# --- REPLACE YOUR 'property_search' FUNCTION WITH THIS ---

def property_search(request):
    """
    View for searching and filtering properties.
    NOW UPGRADED to show Featured listings first AND hide Sold listings.
    """
    
    # --- 1. UPGRADED: Filter/Search Logic (GET) ---
    
    now = timezone.now()

    # --- 1a. THIS IS THE UPGRADE ---
    # We first create a "base queryset" that ONLY includes 'ACTIVE' properties.
    # All other logic (filtering, sorting) will be built on top of this.
    base_queryset = Property.objects.filter(status=PropertyStatus.ACTIVE)
    
    # 1b. Create a "live" featured status
    queryset = base_queryset.annotate( # <-- Use base_queryset here
        is_featured_live=Case(
            When(is_featured=True, featured_until__gte=now, then=True),
            default=False,
            output_field=BooleanField()
        )
    )

    # 1c. This is your new "professional" sort order
    queryset = queryset.order_by('-is_featured_live', '-is_verified', '-created_at')

    # 1d. This part is the same as before
    property_filter = PropertyFilter(request.GET, queryset=queryset)
    
    
    # --- 2. New Logic for Saving the Search (POST) ---
    # (This part is 100% the same as your old code, no changes here)
    saved_search_form = SavedSearchForm() 

    if request.method == 'POST' and request.user.is_authenticated:
        # ... (all your existing POST logic for saving a search) ...
        # ... (no changes are needed here) ...
        saved_search_form = SavedSearchForm(request.POST)
        
        if saved_search_form.is_valid():
            try:
                query_params = request.GET
                search = saved_search_form.save(commit=False)
                search.user = request.user
                
                search.keyword = query_params.get('keyword', None)
                city_id = query_params.get('city', None)
                if city_id:
                    search.city_id = int(city_id)
                search.property_type = query_params.get('property_type', None)
                search.purpose = query_params.get('purpose', None)
                
                try:
                    min_price_str = query_params.get('price_min', None)
                    if min_price_str:
                        search.min_price = Decimal(min_price_str.replace(',', ''))
                except (ValueError, TypeError):
                    pass 
                try:
                    max_price_str = query_params.get('price_max', None)
                    if max_price_str:
                        search.max_price = Decimal(max_price_str.replace(',', ''))
                except (ValueError, TypeError):
                    pass 
                try:
                    min_bed_str = query_params.get('bedrooms_min', None)
                    if min_bed_str:
                        search.min_bedrooms = int(min_bed_str)
                except (ValueError, TypeError):
                    pass 
                
                search.save()
                messages.success(request, f"Your search '{search.name}' has been saved!")
                return redirect(request.get_full_path())
                
            except IntegrityError:
                messages.error(request, "You already have a search with that name. Please choose a different name.")
        
        else:
            messages.error(request, "To save a search, you must give it a name.")

    
    # --- 3. Context for the template ---
    context = {
        'filter': property_filter,
        'saved_search_form': saved_search_form,
    }
    
    return render(request, 'properties/property_search.html', context)
@login_required(login_url='login') 
def property_create(request):
    """
    View for creating a new property listing.
    Now handles multiple gallery image uploads.
    """
    form = PropertyForm()
    
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            
            # Save the main Property object
            property = form.save(commit=False)
            property.agent = request.user 
            property.save()
            
            # --- NEW LOGIC FOR GALLERY IMAGES ---
            # Get the list of files from the 'gallery_images' field
            images = request.FILES.getlist('gallery_images')
            
            # Loop through each file and create a PropertyImage object
            for image in images:
                PropertyImage.objects.create(property=property, image=image)
            # --- END OF NEW LOGIC ---
            
            # Redirect to the detail page of the new property
            return redirect('property_detail', pk=property.pk)
    
    context = {
        'form': form,
        'title': 'Create New Listing'
    }
    return render(request, 'properties/property_form.html', context)

# properties/views.py

# --- REPLACE YOUR OLD 'agent_dashboard' FUNCTION WITH THIS ---

@login_required(login_url='login')
def agent_dashboard(request):
    
    now = timezone.now()
    
    # 1. Get all properties for this agent
    my_properties_qs = Property.objects.filter(agent=request.user)
    
    # 2. Annotate with 'is_featured_live' status
    # This checks if the property is featured AND not expired
    my_properties = my_properties_qs.annotate(
        is_featured_live=Case(
            When(is_featured=True, featured_until__gte=now, then=True),
            default=False,
            output_field=BooleanField()
        )
    ).order_by('-created_at') # Order after annotating
    
    context = {
        'properties': my_properties
    }
    return render(request, 'properties/agent_dashboard.html', context)


# --- REPLACE YOUR OLD 'property_update' FUNCTION WITH THIS ---

@login_required(login_url='login')
def property_update(request, pk):
    """
    Handles the "Edit" functionality for a property.
    This is the corrected version with the proper scope.
    """
    
    # --- THIS IS THE KEY ---
    # We get the property object *before* we check the request method.
    # Now, 'property' is in scope for the entire function.
    property = get_object_or_404(Property, pk=pk)
    
    # --- Security Check ---
    if property.agent != request.user:
        return HttpResponseForbidden()
    
    # --- POST Request Logic (Submitting the form) ---
    if request.method == 'POST':
        
        # We pass in 'instance=property' so the form knows we are updating.
        form = PropertyForm(request.POST, request.FILES, instance=property)
        
        if form.is_valid():
            # This save will update the existing property
            property = form.save() 
            
            # This is our logic to add new gallery images
            images = request.FILES.getlist('gallery_images')
            for image in images:
                PropertyImage.objects.create(property=property, image=image)
            
            # Add a success message
            messages.success(request, 'Your property has been updated successfully!')
            
            return redirect('property_detail', pk=property.pk)
        
        else:
            # If the form is invalid (e.g., missing main_image),
            # we will print the errors to your terminal.
            # The button will still "do nothing," but now we'll know why.
            print("--- FORM IS INVALID (Update View) ---")
            print(form.errors)
            
    # --- GET Request Logic (Just loading the page) ---
    else:
        # We pass in 'instance=property' to pre-fill the form
        # with the existing property's data.
        form = PropertyForm(instance=property)

    # This context is used for both GET and invalid POST requests
    context = {
        'form': form,
        'title': 'Update Your Property'
    }
    return render(request, 'properties/property_form.html', context)

# --- Make sure your delete_property_image view is AFTER this ---
# (The code for delete_property_image was correct)



# this is from delets img in edit or update
# --- ADD THIS NEW VIEW ---

@login_required(login_url='login')
def delete_property_image(request, image_pk):
    """
    Deletes a single gallery image.
    This view is professional:
    1. It only accepts POST requests.
    2. It checks that the logged-in user *owns* the property.
    """

    # 1. We only allow POST requests
    if request.method != 'POST':
        return HttpResponseForbidden("This action requires a POST request.")

    # 2. Find the image or return a 404
    image = get_object_or_404(PropertyImage, pk=image_pk)

    # 3. Security Check: Is this user the owner?
    property = image.property
    if property.agent != request.user:
        return HttpResponseForbidden("You do not have permission to delete this image.")

    # 4. If all checks pass, delete the image
    image.delete()

    # 5. Add a success message
    messages.success(request, 'Image deleted successfully.')

    # 6. Redirect back to the "update" page
    return redirect('property_update', pk=property.pk)

class PropertyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Handles the deletion of a property.
    """
    model = Property
    template_name = 'properties/property_confirm_delete.html'
    success_url = reverse_lazy('agent_dashboard')
    
    def test_func(self):
        property = self.get_object()
        return self.request.user == property.agent
    


    # --- ADD THESE TWO NEW VIEWS for add to favourites and remove ---

@login_required(login_url='login')
def add_to_favorites_view(request, pk):
    """
    Adds a property to the user's favorites list.
    """
    # We only accept POST requests for this action
    if request.method != 'POST':
        return HttpResponseForbidden()

    property = get_object_or_404(Property, pk=pk)
    
    # This is the magic: add the property to the user's favorites
    request.user.favorites.add(property)
    
    messages.success(request, f"'{property.title}' has been added to your favorites.")
    
    # This is a pro-trick: redirect the user back to whatever
    # page they were on (e.g., the homepage or the detail page).
    return redirect(request.META.get('HTTP_REFERER', 'homepage'))


@login_required(login_url='login')
def remove_from_favorites_view(request, pk):
    """
    Removes a property from the user's favorites list.
    """
    if request.method != 'POST':
        return HttpResponseForbidden()

    property = get_object_or_404(Property, pk=pk)
    
    # This is the magic: remove the property from the user's favorites
    request.user.favorites.remove(property)
    
    messages.success(request, f"'{property.title}' has been removed from your favorites.")
    
    return redirect(request.META.get('HTTP_REFERER', 'homepage'))



# ---  TWO VIEWS FOR THE INTERACTIVE MAP ---

def map_search_view(request):
    """
    Step 2: Serves the main interactive map search page.
    This view just renders the template. The template's JavaScript
    will then call the 'property_api_view' to get the data.
    """
    # We will create this template in the next step
    return render(request, 'properties/map_search.html')


def property_api_view(request):
    """
    Step 1: This is the "Data Source" or "API" view.
    It returns a JSON list of all properties that have coordinates.
    """
    try:
        # 1. Efficiently query properties.
        # We use select_related('area') to fetch the related Area
        # in the same database query. This is a huge performance win.
        properties = Property.objects.select_related('area').filter(
            area__latitude__isnull=False,  # Only include properties with a latitude
            area__longitude__isnull=False # Only include properties with a longitude
        ).order_by('-created_at')

        # 2. Build the list of data for the map
        data_list = []
        for prop in properties:
            data_list.append({
                'id': prop.pk,
                'title': prop.title,
                'lat': prop.area.latitude,
                'lng': prop.area.longitude,
                'price': f"PKR {intcomma(prop.price)}", # e.g., "PKR 50,000,000"
                'area_name': str(prop.area),
                
                # Get image URL, but check if main_image exists first
                'image_url': prop.main_image.url if prop.main_image else None,
                
                # Get the URL to the property's detail page
                'detail_url': reverse('property_detail', args=[prop.pk])
            })
        
        # 3. Return the list as a JSON response
        return JsonResponse(data_list, safe=False)
    
    except Exception as e:
        # Handle any potential errors
        return JsonResponse({'error': str(e)}, status=500)


# --- ADD THIS NEW VIEW FOR THE AI ASSISTANT ---
# properties/views.py (at the bottom)



@login_required
@require_POST # This view should only accept POST requests
def generate_ai_description(request):
    """
    An API view that receives property data (as JSON),
    sends it to the Gemini AI, and returns a generated description.
    """
    try:
        # 1. Get the data from the JavaScript 'fetch' request
        data = json.loads(request.body)
        
        # 2. Extract the data (with defaults to prevent errors)
        purpose = data.get('purpose', '')
        property_type = data.get('property_type', '')
        city = data.get('city', '')
        area = data.get('area', '')
        bedrooms = data.get('bedrooms', 'any')
        bathrooms = data.get('bathrooms', 'any')
        area_size = data.get('area_size', '')
        area_unit = data.get('area_unit', '')
        price = data.get('price', '')

        # 3. Create a professional prompt for the AI
        prompt = f"""
        Write a compelling and professional real estate listing description.
        - The property is {purpose} and is a {property_type}.
        - It is located in {area}, {city}.
        - It has {bedrooms} bedrooms and {bathrooms} bathrooms.
        - The size is {area_size} {area_unit}.
        - The price is PKR {price}.
        
        Based on this data, write an attractive description.and use simple words and remember dont write like these lines on top like here is yout description  only write requide description
        and write short and simple words
        - Use strong, positive adjectives.
        - Highlight the key features (bedrooms, bathrooms, location).
        - DO NOT include the price in the final description.
        - The tone should be professional and inviting.
        - Do not just list the facts; write 2-3 engaging paragraphs.
        """
        
        # 4. Send the prompt to the AI
        #
        # === THIS IS THE FINAL FIX ===
        # We are using the correct model name you found from the list.
        #
        model = genai.GenerativeModel('models/gemini-2.5-pro')
        response = model.generate_content(prompt)
        
        # 5. Return the AI's text as a JSON response
        return JsonResponse({'description': response.text})

    except Exception as e:
        # Handle any errors
        return JsonResponse({'error': str(e)}, status=500)
    

# --- ADD THIS NEW VIEW FOR YOUR "HOW TO PAY" PAGE ---

@login_required
def boost_listing_info(request):
    """
    A simple, static page that explains to an agent
    how to pay for a featured listing.
    """
    # We will create this template in Step 3
    return render(request, 'properties/boost_listing_info.html')


# --- ADD THIS NEW VIEW FOR MARKING A PROPERTY AS SOLD ---

@login_required
@require_POST # This action must be a POST request
def mark_as_sold_view(request, pk):
    """
    Handles an agent marking their own property as 'Sold'.
    """
    # 1. Get the property and check for a 404
    prop = get_object_or_404(Property, pk=pk)
    
    # 2. Security Check: Is this agent the owner?
    if prop.agent != request.user:
        messages.error(request, "You do not have permission to modify this listing.")
        return redirect('agent_dashboard')
        
    # 3. Update the property's status
    prop.status = PropertyStatus.SOLD
    prop.sold_date = timezone.now() # Record the time it was sold
    prop.is_featured = False # A sold property cannot be featured
    prop.save()
    
    # 4. Send a success message and redirect
    messages.success(request, f"'{prop.title}' has been successfully marked as sold.")
    return redirect('agent_dashboard')

# --- ADD THESE THREE NEW VIEWS FOR THE "COMPARE" FEATURE ---

def compare_page_view(request):
    """
    Step 1.3: The main page that shows the comparison table.
    """
    compare_ids = request.session.get('compare_list', [])
    properties_to_compare = Property.objects.filter(pk__in=compare_ids)
    
    context = {
        'properties': properties_to_compare
    }
    # We will create this template in the next step
    return render(request, 'properties/compare_page.html', context)


@require_POST # This action must be a POST request
def add_to_compare_view(request, pk):
    """
    Step 1.1: Adds a property ID to the comparison list in the session.
    NOW RETURNS JSON for our JavaScript.
    """
    compare_list = request.session.get('compare_list', [])
    property_id = pk
    
    if property_id not in compare_list:
        if len(compare_list) >= 4:
            # If the list is full (4 items), remove the oldest item first
            compare_list.pop(0) 
        compare_list.append(property_id)
        
    request.session['compare_list'] = compare_list
    
    # Return a JSON response with the new count
    return JsonResponse({'status': 'added', 'compare_list_count': len(compare_list)})




# new for remove from comapare feature

@require_POST
def remove_from_compare_view(request, pk):
    """
    Removes a property ID from the comparison list in the session.
    
    NOW "SMARTER":
    - If it's an AJAX (JavaScript) request, it returns JSON.
    - If it's a normal form submission, it redirects.
    """
    compare_list = request.session.get('compare_list', [])
    property_id = pk
    
    try:
        compare_list.remove(property_id)
        messages.success(request, "Property removed from comparison list.")
    except ValueError:
        pass 
        
    request.session['compare_list'] = compare_list
    
    # --- THIS IS THE FIX ---
    # Check if this is an AJAX request (from our search page's JavaScript)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # If YES, return JSON for the JavaScript to handle
        return JsonResponse({'status': 'removed', 'compare_list_count': len(compare_list)})
    else:
        # If NO (it's a form from the compare page),
        # redirect back to the compare page.
        return redirect('compare_page')