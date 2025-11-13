from django import forms
from .models import Question, Answer

class QuestionForm(forms.ModelForm):
    """
    A form for a user to submit a new Question about an Area.
    """
    class Meta:
        model = Question
        # We only want the user to fill out these two fields
        fields = ['title', 'body']
        
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., What is the internet quality like in this area?'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Add some more details to your question (optional)...'
            }),
        }
        labels = {
            'title': 'Your Question:',
            'body': 'Details (Optional):',
        }

    def __init__(self, *args, **kwargs):
        """
        This function runs when the form is created.
        We use it to make the 'body' (details) field optional.
        """
        super().__init__(*args, **kwargs)
        self.fields['body'].required = False


class AnswerForm(forms.ModelForm):
    """
    A simple form for a user to submit an Answer to a Question.
    """
    class Meta:
        model = Answer
        # The user only needs to provide the 'body' of the answer
        fields = ['body']
        
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your answer...'
            }),
        }
        labels = {
            'body': '', # We hide the label, the placeholder is enough
        }