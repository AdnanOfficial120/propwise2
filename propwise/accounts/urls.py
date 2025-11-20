from django.urls import path
from django.contrib.auth import views as auth_views
from . import views as account_views

urlpatterns = [
    # 1. Sign Up
    path('signup/', account_views.SignUpView.as_view(), name='signup'),
    
    # 2. Log In
    path('login/', 
         auth_views.LoginView.as_view(
             template_name='accounts/login.html',
             redirect_authenticated_user=True 
         ), 
         name='login'),
         
    # 3. Log Out
    path('logout/', 
         auth_views.LogoutView.as_view(
             next_page='homepage'  
         ), 
         name='logout'),

    # 4. Profile & Saved
    path('profile/', account_views.profile_view, name='profile'),
    path('saved/', account_views.saved_properties_view, name='saved_properties'),
   
    # 5. Agent Directory & Public Profile
    path('agents/', account_views.agent_directory_view, name='agent_directory'),
    path('agent/<int:pk>/', account_views.agent_profile_view, name='agent_profile'),
    
    # 6. Notification "Mark as Read"
    path('notification/<int:pk>/read/', account_views.mark_notification_read, name='mark_notification_read'),

    # 7. LEAD MANAGER URLS
    path('my-leads/', account_views.lead_manager_view, name='my_leads'),
    path('my-leads/edit/<int:pk>/', account_views.update_lead_view, name='update_lead'),
    path('my-leads/delete/<int:pk>/', account_views.delete_lead_view, name='delete_lead'),
    
    # 8. VISIT SCHEDULING
    path('schedule-visit/<int:property_pk>/', account_views.schedule_visit_view, name='schedule_visit'),

    # --- START: PASSWORD RESET URLS ---
    
    # 1. Enter Email Page
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset_form.html'
         ), 
         name='password_reset'),

    # 2. "Check your Email" Page
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ), 
         name='password_reset_done'),

    # 3. Enter New Password Page (Link from Email)
    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ), 
         name='password_reset_confirm'),

    # 4. Success Page
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ), 
         name='password_reset_complete'),

    # --- END: PASSWORD RESET URLS ---
]