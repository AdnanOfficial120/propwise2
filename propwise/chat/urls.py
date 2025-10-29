# chat/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # This will be the URL: /chat/inbox/
    path('inbox/', views.chat_inbox_view, name='chat_inbox'),
    
    # /chat/start/<int:property_pk>/
    path('start/<int:property_pk>/', views.start_chat_view, name='start_chat'),
    
    # /chat/detail/<int:thread_id>/
    path('detail/<int:thread_id>/', views.chat_detail_view, name='chat_detail'),
]