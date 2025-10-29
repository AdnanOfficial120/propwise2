# locations/admin.py

from django.contrib import admin
from .models import City, Area

# Register your models here.
admin.site.register(City)
admin.site.register(Area)