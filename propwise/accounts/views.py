# accounts/views.py

from django.shortcuts import render, redirect,get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm
from django.contrib.auth import login,authenticate, logout # Import the 
from django.contrib import messages
from .forms import CustomUserChangeForm
from django.contrib.auth.decorators import login_required
# these import to show agent info   
from django.contrib.auth import get_user_model
from properties.models import Property



User = get_user_model() # Make sure this is defined for agent info..
class SignUpView(generic.CreateView):
    """
    This is a class-based view that handles user registration.
    """
    form_class = CustomUserCreationForm
    # We use reverse_lazy for the redirect URL
    success_url = reverse_lazy('homepage') 
    template_name = 'accounts/signup.html'

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        user = form.save()
        # Log the user in directly after signing up
        login(self.request, user)
        return super().form_valid(form)
    

    # --- ADD THIS NEW VIEW FUNCTION ---

@login_required(login_url='login')
def profile_view(request):
    """
    Handles the user profile page and form.
    """

    
    if request.method == 'POST':
        # We pass in the POST data, the FILES data (for the image),
        # and 'instance=request.user' to tell Django *which* user to update.
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('homepage') # Redirect back to the same page

    # This is the logic for SHOWING the form
    else:
        # We pass 'instance=request.user' to pre-fill the form
        # with the current user's information.
        form = CustomUserChangeForm(instance=request.user)

    
    context = {
        'form': form
    }

    #
    return render(request, 'accounts/profile.html', context)


# --- ADDed THIS NEW VIEW  to seee save or like properties---

@login_required(login_url='login')
def saved_properties_view(request):
    """
    Displays all properties favorited by the current user.
    """
    
    # This is the magic. We get all properties from the user's
    # 'favorites' list and order them by the newest.
    saved_list = request.user.favorites.order_by('-created_at')
    
    context = {
        'properties': saved_list
    }
    
    # We'll create this template in the next step
    return render(request, 'accounts/saved_properties.html', context)




# this is for show agent info# --- ADD THIS NEW VIEW ---

def agent_profile_view(request, pk):
    """
    Displays the public profile for a single agent,
    including all of their active listings.
    """
    
    # --- Professional Query ---
    # We get the User, but we also *require* them to be an agent.
    # If a user tries to view a profile of a non-agent, they get a 404.
    agent = get_object_or_404(User, pk=pk, is_agent=True)
    
    # --- Get all properties listed by this one agent ---
    agent_properties = Property.objects.filter(agent=agent).order_by('-created_at')
    
    context = {
        'agent': agent,
        'properties': agent_properties # Pass the properties to the template
    }
    
    # We'll create this template in the next step
    return render(request, 'accounts/agent_profile.html', context)
    