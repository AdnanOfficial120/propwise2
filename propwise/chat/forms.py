# chat/forms.py

from django import forms
from .models import ChatMessage

class ChatMessageForm(forms.ModelForm):
    """
    A simple form for sending a new chat message.
    """
    class Meta:
        model = ChatMessage
        fields = ['body'] # We only want the user to type the 'body'

        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control', # For Bootstrap styling (if you use it)
                'rows': 3,
                'placeholder': 'Type your message here...',
                'style': 'width: 100%; padding: 10px; border-radius: 8px; border: 1px solid #ccc;',
            })
        }
        # We remove the <label> for the body field
        labels = {
            'body': '', 
        }