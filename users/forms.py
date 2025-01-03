from django import forms
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    agree_to_terms = forms.BooleanField(required=True, label="I agree to the terms and conditions.")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'bio']

