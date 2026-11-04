
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Project, Milestone, Task


# Registration Form
class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# Project Form
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'description',
            'start_date',
            'due_date',
            'status',
        ]

        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


# Milestone Form
class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = [
            'title',
            'description',
            'due_date',
            'status',
        ]

        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }


# Task Form
class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title',
            'description',
            'completed',
        ]

