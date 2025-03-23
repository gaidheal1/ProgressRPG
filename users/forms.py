from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
import logging 

from .models import CustomUser, Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    agree_to_terms = forms.BooleanField(required=True, label="I agree to the terms and conditions.")

    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2']


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email address', max_length=254)

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if email and password:
            self.user_cache = authenticate(username=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data
                               
class ProfileForm(forms.ModelForm):
    name = forms.CharField(required=True, label="Required. Enter a username.")

    class Meta:
        model = Profile
        fields = ['name', 'bio']

