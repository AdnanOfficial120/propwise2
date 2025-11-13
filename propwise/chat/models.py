# chat/models.py

from django.db import models
from django.contrib.auth import get_user_model
from properties.models import Property  # Import the Property model


User = get_user_model()

class ChatThread(models.Model):
    """
    A model to represent a single chat thread.
    It connects a property, a buyer, and an agent.
    """
    # --- PROFESSIONAL CHANGE 1 ---
    # If the property is deleted, we SET_NULL. This PRESERVES the chat history.
    property = models.ForeignKey(
        Property, 
        on_delete=models.SET_NULL,  # <-- NOT CASCADE
        related_name='chat_threads',
        null=True,  # <-- Required for SET_NULL
        blank=True  # <-- Allows this to be empty in forms
    )
    
    buyer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,  # Cascade is OK here. If a buyer is deleted, their threads go.
        related_name='bought_chat_threads'
    )
    
    agent = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,  # Cascade is OK here. If an agent is deleted, their threads go.
        related_name='agent_chat_threads'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        prop_title = self.property.title if self.property else "Deleted Property"
        return f"Chat about '{prop_title}' between {self.buyer.username} and {self.agent.username}"

    class Meta:
        # This ensures that a buyer can only start ONE chat thread
        # for a specific property with a specific agent.
        unique_together = ('property', 'buyer', 'agent')


class ChatMessage(models.Model):
    """
    A single message within a chat thread.
    """
    thread = models.ForeignKey(
        ChatThread, 
        on_delete=models.CASCADE,  # If the thread is gone, messages are gone. This is correct.
        related_name='messages'
    )
    
    # --- PROFESSIONAL CHANGE 2 ---
    # If the sender's account is deleted, we SET_NULL.
    # This keeps the message in the chat, attributed to a "Deleted User".
    sender = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,  # <-- NOT CASCADE
        related_name='sent_messages',
        null=True # <-- Required for SET_NULL
    )
    
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # --- PROFESSIONAL CHANGE 3 ---
    # This is the new, crucial field for "read receipts".
    is_read = models.BooleanField(default=False)

    def __str__(self):
        sender_name = self.sender.username if self.sender else "Deleted User"
        return f"Message from {sender_name} in thread {self.thread.id}"

    class Meta:
        ordering = ['timestamp'] # Show newest messages last