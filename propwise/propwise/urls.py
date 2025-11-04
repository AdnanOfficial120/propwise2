"""
URL configuration for propwise project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('listings/', include('properties.urls')),
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chat.urls')),
    path('locations/', include('locations.urls')),
]

# propwise/urls.py

# --- Import this at the top with your other imports ---
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# ... (your main urlpatterns list) ...

if settings.DEBUG:
    # This serves your user-uploaded media files (like profile pictures)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # --- THIS IS THE NEW FIX ---
    # This manually adds the serving of static files (like .js and .css)
    # This will fix the 404 error for both your file and the debug toolbar
    urlpatterns += staticfiles_urlpatterns()



# --- 2. ADD THIS NEW BLOCK ---
    # This adds the Debug Toolbar's URLs ONLY in debug mode
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    # --- END OF NEW BLOCK -
