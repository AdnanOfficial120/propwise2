# locations/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Page 1: /locations/
    path('', views.all_cities_view, name='all_cities'),
    
    # Page 2: /locations/1/ (or 2, 3, etc.)
    path('<int:city_pk>/', views.city_detail_view, name='city_detail'),
    # Page 3: /locations/area/5/ (or 6, 7, etc.)
    path('area/<int:area_pk>/', views.area_detail_view, name='area_detail'),
]