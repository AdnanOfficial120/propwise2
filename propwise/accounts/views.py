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
#  for rating system 
from .forms import AgentRatingForm # Our new review form
from django.db.models import Avg, Count # To calculate the average rating
from django.db import IntegrityError # To catch duplicate reviews
from .models import Notification # Make sure Notification is imported
from .models import AgentRating, Lead, Notification, VisitRequest, LeadStatus # <-- ADD VisitRequest, LeadStatus
from .forms import AgentRatingForm, LeadForm, VisitRequestForm # <-- ADD VisitRequestForm
from django.urls import reverse






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

# accounts/views.py

# --- REPLACE YOUR OLD 'agent_profile_view' WITH THIS NEW VERSION ---

def agent_profile_view(request, pk):
    """
    Displays the public profile for a single agent,
    including all of their active listings,
    AND handles the review/rating system.
    """
    
    # 1. Get the agent (same as before)
    agent = get_object_or_404(User, pk=pk, is_agent=True)
    
    # --- 2. Handle a New Review Submission (POST Request) ---
    
    # We initialize review_form as None here.
    # If the request is GET, we'll create an empty one later.
    # If the request is POST, we'll populate it here.
    review_form = None 
    
    if request.method == 'POST':
        # Security: User must be logged in to post a review
        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to leave a review.')
            return redirect('login') # Redirect to login

        # Security: An agent cannot review themselves
        if request.user == agent:
            messages.error(request, "You cannot review your own profile.")
            return redirect('agent_profile', pk=agent.pk)
        
        # Security: Only buyers can leave reviews (optional, but good practice)
        if not request.user.is_buyer:
            messages.error(request, "Only buyers are eligible to leave reviews.")
            return redirect('agent_profile', pk=agent.pk)

        # Process the form
        review_form = AgentRatingForm(request.POST)
        if review_form.is_valid():
            try:
                # We use 'try/except' to catch the 'unique_together'
                # constraint from our model. This stops duplicate reviews.
                new_review = review_form.save(commit=False)
                new_review.agent = agent       # The agent being reviewed
                new_review.reviewer = request.user # The user writing the review
                new_review.save()
                
                messages.success(request, 'Your review has been submitted successfully!')
            
            except IntegrityError:
                # This error happens if the (agent, reviewer) pair already exists
                messages.error(request, 'You have already reviewed this agent.')
            
            # Always redirect after a successful POST to prevent re-submission
            return redirect('agent_profile', pk=agent.pk)
        
        # If review_form is NOT valid, we just fall through to the
        # GET logic, and the *invalid* form (with error messages)
        # will be passed to the template.

    # --- 3. Prepare Data for Page Load (GET Request) ---

    # Get properties (same as before)
    agent_properties = Property.objects.filter(agent=agent).order_by('-created_at')

    # Get all reviews for this agent
    all_reviews = AgentRating.objects.filter(agent=agent)
    
    # Calculate the average rating and total count
    # .aggregate() is the most efficient way to do this
    rating_stats = all_reviews.aggregate(
        avg_rating=Avg('rating'), 
        total_reviews=Count('rating')
    )
    
    # --- 4. Determine if the current user can post a review ---
    
    user_can_review = False
    user_has_reviewed = False
    
    if request.user.is_authenticated:
        # Check if the user has already left a review
        if all_reviews.filter(reviewer=request.user).exists():
            user_has_reviewed = True
        
        # Check if user is eligible to review:
        # They must be a buyer, not be the agent, and not have reviewed yet.
        if request.user.is_buyer and request.user != agent and not user_has_reviewed:
            user_can_review = True

    # --- 5. Create the review form for the template ---
    
    # If this is a GET request, create a new, empty form
    if review_form is None:
        review_form = AgentRatingForm()

    # --- 6. Build the final context ---
    context = {
        'agent': agent,
        'properties': agent_properties,
        
        # New context variables for the rating system
        'all_reviews': all_reviews,
        'rating_stats': rating_stats,        # e.g., {'avg_rating': 4.5, 'total_reviews': 10}
        'user_can_review': user_can_review,  # True/False
        'user_has_reviewed': user_has_reviewed, # True/False
        'review_form': review_form,          # The form to add a review
    }
    
    return render(request, 'accounts/agent_profile.html', context)

# --- ADD THIS NEW VIEW FOR THE AGENT DIRECTORY  reviewing system start---

def agent_directory_view(request):
    """
    Displays a public-facing list of all registered agents.
    This is Part 1 of our "Agent Directory" feature.
    """

    # 1. Get all users who have 'is_agent' set to True
    # We also order them by first name, last name, and username
    # so the list is neatly organized.
    all_agents = User.objects.filter(
        is_agent=True
    ).order_by('first_name', 'last_name', 'username')

    # 2. Pass this list of agents into the template context
    context = {
        'agents': all_agents
    }

    # 3. We will create this template in the next step
    return render(request, 'accounts/agent_directory.html', context)
    



    

# ---  VIEW FOR THE "LEAD MANAGER" ---

# accounts/views.py

# --- 1. ADD 'LeadForm' TO YOUR IMPORTS ---
# Find your other form imports and add 'LeadForm'
from .forms import CustomUserCreationForm, CustomUserChangeForm, SavedSearchForm, AgentRatingForm, LeadForm


# --- 'lead_manager_view'  ---

@login_required(login_url='login')
def lead_manager_view(request):
    """
    Shows the currently logged-in agent their private list of leads
    AND handles the form for adding a new lead.
    """
    
    # 1. Security: Only agents can access this page
    if not request.user.is_agent:
        messages.error(request, "This page is only for registered agents.")
        return redirect('homepage') 
        
    # --- 2. NEW: Handle Form Submission (POST Request) ---
    if request.method == 'POST':
        # We pass 'agent=request.user' to the form's __init__
        # so it can filter the property dropdown
        form = LeadForm(request.POST, agent=request.user)
        
        if form.is_valid():
            # Create the Lead object but don't save to DB yet
            lead = form.save(commit=False)
            # Set the agent (the current user)
            lead.agent = request.user 
            lead.save()
            
            messages.success(request, f"New lead '{lead.contact_name}' has been added.")
            return redirect('my_leads') # Redirect to clear the form
        else:
            # If the form is invalid, we'll fall through and
            # render the page with the form's error messages
            messages.error(request, "Please correct the errors below.")
    else:
        # --- This is a GET request ---
        # Create a new, blank form, passing in the agent
        form = LeadForm(agent=request.user)
        
    # --- 3. Get all leads (Same as before) ---
    agent_leads = Lead.objects.filter(agent=request.user).order_by('-created_at')
    
    # --- 4. Update the Context ---
    context = {
        'leads': agent_leads,
        'form': form, # <-- Add the form to the context
    }
    
    return render(request, 'accounts/my_leads.html', context)

# --- ADD THIS NEW VIEW TO MARK NOTIFICATIONS AS READ ---

@login_required
def mark_notification_read(request, pk):
    """
    1. Gets the notification object.
    2. Checks if the current user owns it.
    3. Marks it as read.
    4. Redirects to the actual link.
    """
    notification = get_object_or_404(Notification, pk=pk)

    # Security: Only the recipient can mark it as read
    if request.user == notification.recipient:
        notification.is_read = True
        notification.save()
        return redirect(notification.link_url)
    
    # If security fails, just go home
    return redirect('homepage')



# --- added THIS VIEW FOR SCHEDULING VISITS  ---

@login_required
def schedule_visit_view(request, property_pk):
    """
    Handles the submission of the "Schedule a Tour" form.
    1. Saves the VisitRequest.
    2. Creates a Lead for the agent.
    3. Notifies the agent.
    """
    property_obj = get_object_or_404(Property, pk=property_pk)
    
    if request.method == 'POST':
        form = VisitRequestForm(request.POST)
        if form.is_valid():
            # 1. Save the Visit Request
            visit = form.save(commit=False)
            visit.buyer = request.user
            visit.agent = property_obj.agent
            visit.property = property_obj
            visit.save()
            
            # 2. Create a Lead for the Agent (Automation)
            try:
                Lead.objects.create(
                    agent=property_obj.agent,
                    contact_name=request.user.get_full_name() or request.user.username,
                    contact_email=request.user.email,
                    contact_phone=request.user.phone_number,
                    status=LeadStatus.NEW,
                    source=f"Visit Request ({property_obj.title})",
                    property_of_interest=property_obj,
                    notes=f"Requested a visit on: {visit.visit_date}. Message: {visit.message}"
                )
            except Exception as e:
                print(f"Error creating lead: {e}")

            # 3. Notify the Agent (Automation)
            Notification.objects.create(
                recipient=property_obj.agent,
                message=f"New Visit Request! {request.user.username} wants to see '{property_obj.title}'",
                link_url=reverse('my_leads') 
            )

            messages.success(request, "Your visit request has been sent! The agent will contact you shortly.")
        else:
            messages.error(request, "There was an error with your request. Please check the date and time.")
            
    # Redirect back to the property page
    return redirect('property_detail', pk=property_pk)