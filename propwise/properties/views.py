# properties/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Property, PropertyImage  # Make sure PropertyImage is imported
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

def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    gallery_images = property.images.all()
    
    context = {
        'property': property,
        'gallery_images': gallery_images,
    }
    
    return render(request, 'properties/property_detail.html', context)

# properties/views.py

# --- REPLACE YOUR OLD 'property_search' FUNCTION WITH THIS ---

def property_search(request):
    """
    View for searching and filtering properties.
    NOW ALSO HANDLES SAVING THE SEARCH via a POST request.
    """
    
    # --- 1. Existing Filter/Search Logic (GET) ---
    # This part is exactly the same as your old code
    queryset = Property.objects.all().order_by('-created_at')
    property_filter = PropertyFilter(request.GET, queryset=queryset)
    
    # --- 2. New Logic for Saving the Search (POST) ---
    saved_search_form = SavedSearchForm() # Initialize empty form for the template

    # We only save a search if the user is logged in AND is submitting the save form
    if request.method == 'POST' and request.user.is_authenticated:
        saved_search_form = SavedSearchForm(request.POST)
        
        if saved_search_form.is_valid():
            try:
                # Get the filter data *from the URL query string* (request.GET)
                query_params = request.GET
                
                search = saved_search_form.save(commit=False)
                search.user = request.user
                
                # --- Populate the search object from the URL filters ---
                search.keyword = query_params.get('keyword', None)
                
                city_id = query_params.get('city', None)
                if city_id:
                    search.city_id = int(city_id)
                    
                search.property_type = query_params.get('property_type', None)
                search.purpose = query_params.get('purpose', None)
                
                # --- Safely convert numeric fields ---
                # This stops the site from crashing if the URL has bad data
                try:
                    min_price_str = query_params.get('price_min', None)
                    if min_price_str:
                        search.min_price = Decimal(min_price_str.replace(',', ''))
                except (ValueError, TypeError):
                    pass # Ignore invalid min_price data
                    
                try:
                    max_price_str = query_params.get('price_max', None)
                    if max_price_str:
                        search.max_price = Decimal(max_price_str.replace(',', ''))
                except (ValueError, TypeError):
                    pass # Ignore invalid max_price data
                
                try:
                    min_bed_str = query_params.get('bedrooms_min', None)
                    if min_bed_str:
                        search.min_bedrooms = int(min_bed_str)
                except (ValueError, TypeError):
                    pass # Ignore invalid bedroom data
                
                # --- End of populating ---
                
                search.save()
                messages.success(request, f"Your search '{search.name}' has been saved!")
                
                # Redirect back to the exact same page (with query string)
                # This stops a re-post if the user hits "refresh"
                return redirect(request.get_full_path())
                
            except IntegrityError:
                messages.error(request, "You already have a search with that name. Please choose a different name.")
        
        else:
            # Form was invalid (user likely didn't enter a name)
            messages.error(request, "To save a search, you must give it a name.")
    
    
    # --- 3. Context for the template ---
    # We now pass the form into the template
    context = {
        'filter': property_filter,
        'saved_search_form': saved_search_form, # Pass the form to the template
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

@login_required(login_url='login')
def agent_dashboard(request):
    my_properties = Property.objects.filter(agent=request.user).order_by('-created_at')
    
    context = {
        'properties': my_properties
    }
    return render(request, 'properties/agent_dashboard.html', context)
# properties/views.py


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