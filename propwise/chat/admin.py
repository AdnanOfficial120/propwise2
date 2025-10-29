# chat/admin.py

from django.contrib import admin
from .models import ChatThread, ChatMessage

class ChatMessageInline(admin.TabularInline):
    """
    Allows us to see and edit messages directly
    from the ChatThread admin page.
    """
    model = ChatMessage
    fields = ('sender', 'body', 'is_read', 'timestamp')
    readonly_fields = ('timestamp',)
    extra = 0 # Don't show any blank "new message" forms

@admin.register(ChatThread)
class ChatThreadAdmin(admin.ModelAdmin):
    """
    Configuration for the ChatThread model in the admin.
    """
    list_display = ('id', 'property', 'buyer', 'agent', 'updated_at')
    list_filter = ('agent', 'buyer')
    search_fields = ('property__title', 'buyer__username', 'agent__username')
    inlines = [ChatMessageInline] # This is the magic line

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Configuration for the ChatMessage model in the admin.
    """
    list_display = ('id', 'thread', 'sender', 'is_read', 'timestamp')
    list_filter = ('is_read', 'sender')
    search_fields = ('body', 'thread__property__title')
    readonly_fields = ('timestamp',)