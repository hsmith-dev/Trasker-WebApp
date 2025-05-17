# trasker_app/forms.py
from django import forms
from .models import Task  # Import your Task model

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        # Specify which fields from the Task model should be in the form
        # Option 1: Include all fields (generally not recommended for user-facing forms without review)
        # fields = '__all__'

        # Option 2: Specify the fields you want to include
        fields = ['title', 'description', 'due_date', 'status', 'priority', 'team'] # Add/remove fields as needed
        # e.g., if 'user' should be set automatically, don't include it here.
        # If 'team' should be a selection, make sure the 'team' field in your Task model is a ForeignKey.

        # Optional: You can customize widgets if needed
        # widgets = {
        #     'due_date': forms.DateInput(attrs={'type': 'date'}),
        #     'description': forms.Textarea(attrs={'rows': 3}),
        # }

    # You can add custom validation methods here if needed
    # def clean_title(self):
    #     title = self.cleaned_data.get('title')
    #     if len(title) < 5:
    #         raise forms.ValidationError("Title must be at least 5 characters long.")
    #     return title