

from django.urls import path
from . import views  # Imports views.py from this (core) app

urlpatterns = [
    # This maps the root URL of the app ('') to our 'homepage' view
    path('', views.homepage, name='homepage'),
]