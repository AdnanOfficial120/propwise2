# accounts/views.py

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from .forms import CustomUserCreationForm
from django.contrib.auth import login,authenticate, logout # Import the 
from django.contrib import messages
from .forms import CustomUserChangeForm
from django.contrib.auth.decorators import login_required

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

    # We pass the form into the template
    context = {
        'form': form
    }

    #
    return render(request, 'accounts/profile.html', context)
    