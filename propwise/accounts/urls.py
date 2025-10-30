
from django.urls import path
from django.contrib.auth import views as auth_views  
from . import views as account_views  # Import our custom signup view

urlpatterns = [
    # 1. Sign Up (Our custom view)
    path('signup/', account_views.SignUpView.as_view(), name='signup'),
    
    # 2. Log In (Django's built-in view)
    path('login/', 
         auth_views.LoginView.as_view(
             template_name='accounts/login.html',
             redirect_authenticated_user=True 
         ), 
         name='login'),
         
    # 3. Log Out (Django's built-in view)
    path('logout/', 
         auth_views.LogoutView.as_view(
             next_page='homepage'  
         ), 
         name='logout'),
    path('profile/', account_views.profile_view, name='profile'),
    # /accounts/saved/
    path('saved/', account_views.saved_properties_view, name='saved_properties'),
    # --- ADDed THIS NEW LINE for show agent info ---
    # /accounts/agent/5/
    path('agent/<int:pk>/', account_views.agent_profile_view, name='agent_profile'),
         
]