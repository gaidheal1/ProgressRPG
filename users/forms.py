from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
import logging 

from .models import CustomUser, Profile

logger = logging.getLogger("django")

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    agree_to_terms = forms.BooleanField(required=True, label="I agree to the terms and conditions.")

    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2']

        


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email address', max_length=254)

    def clean(self):
        try:
            email = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            logger.info(f"[EMAIL AUTHENTICATION FORM] Attempting authentication for email {email}.")

            if email and password:
                self.user_cache = authenticate(username=email, password=password)
                if self.user_cache is None:
                    logger.warning(f"[EMAIL AUTHENTICATION FORM] Authentication failed for email {email}.")
                    raise forms.ValidationError(
                        self.error_messages['invalid_login'],
                        code='invalid_login',
                        params={'username': self.username_field.verbose_name},
                    )
                else:
                    logger.debug(f"[EMAIL AUTHENTICATION FORM] Authentication successful for email {email}.")
                    self.confirm_login_allowed(self.user_cache)
            return self.cleaned_data
        except forms.ValidationError as e:
            logger.error(f"[EMAIL AUTHENTICATION FORM] Validation error: {e}")
            raise
        except Exception as e:
            logger.error(f"[EMAIL AUTHENTICATION FORM] Unexpected error: {e}")
            raise forms.ValidationError("An unexpected error occurred during authentication.")
                               
class ProfileForm(forms.ModelForm):
    name = forms.CharField(required=True, label="Required. Enter a username.")

    class Meta:
        model = Profile
        fields = ['name', 'bio']

