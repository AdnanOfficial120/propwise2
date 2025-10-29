# properties/urls.py (NEW FILE)

from django.urls import path
from . import views

urlpatterns = [

    path('property/<int:pk>/', views.property_detail, name='property_detail'),
    path('search/', views.property_search, name='property_search'),
    path('create/', views.property_create, name='property_create'),
    # My Dashboard"  edit        and "Update" Views edittt pathh

    path('dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('update/<int:pk>/', views.property_update, name='property_update'),
    # for delete post in by agents 
    # We use .as_view() because it is a Class-Based View
    path('delete/<int:pk>/', views.PropertyDeleteView.as_view(), name='property_delete'),
    # e.g., /listings/image/delete/123/
    path('image/delete/<int:image_pk>/', views.delete_property_image, name='delete_property_image'),

]