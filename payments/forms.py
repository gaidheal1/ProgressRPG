from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = subscription
        fields = ['bio', 'profile_picture']

