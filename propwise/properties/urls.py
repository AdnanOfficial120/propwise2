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
    # /listings/add-favorite/5/
    path('add-favorite/<int:pk>/', views.add_to_favorites_view, name='add_to_favorites'),
    # /listings/remove-favorite/5/
    path('remove-favorite/<int:pk>/', views.remove_from_favorites_view, name='remove_from_favorites'),
    # --- TWO NEW URLS FOR THE MAP SEARCH ---
    # 1. The public-facing page that shows the map
    # 1. The page that shows the map (You probably have this one)
    path('map/', views.map_search_view, name='map_search'),
    
    # 2. The data source for the map (THIS IS THE MISSING ONE)
    path('api/properties/', views.property_api_view, name='property_api'),
    # --- ADD THIS NEW LINE FOR THE AI ASSISTANT ---
    path('api/generate-description/', views.generate_ai_description, name='generate_ai_description'),
    # --- ADD THIS NEW LINE FOR THE "BOOST" PAGE ---
    path('boost-info/', views.boost_listing_info, name='boost_listing_info'),
    # --- ADD THIS NEW LINE FOR THE "SOLD" BUTTON ---
    path('mark-as-sold/<int:pk>/', views.mark_as_sold_view, name='mark_as_sold'),
]

