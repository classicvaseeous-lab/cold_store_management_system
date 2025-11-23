from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label="Email or Username")
    # password = forms.CharField(label="Password", widget=forms.PasswordInput)