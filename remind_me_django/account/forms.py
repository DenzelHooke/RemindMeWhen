from django import forms
from django.forms import ModelForm, TextInput, EmailInput, Textarea
from django.contrib.auth.forms import AuthenticationForm, UsernameField
from .models import CustomUser, Profile
from django.utils.translation import ugettext_lazy as _


class UserUpdateForm(forms.ModelForm):
    # Not needed, but without it, our email field form won't check for email validation.
    email_label = 'Email'
    
    email = forms.EmailField(label=email_label, 
        widget=forms.TextInput(attrs={'placeholder': 'Email address', 'class':'input-field'}),
        )

    class Meta:
        model = CustomUser
        # Tells our form that we want to work with the email fields
        fields = ['email']

        widgets = {
            'email': TextInput(attrs={'placeholder':'Optional product name', 'class':'input-field'}),
        }

class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['image', 'bio']

        widgets = {
            'bio': Textarea(attrs={'placeholder':'Enter something ominous..', 'class':'input-field'}),
        }

class UserAuthForm(AuthenticationForm):

    username = UsernameField(widget=TextInput(attrs={'placeholder': '','autofocus': True, 'class':'input-field'}))

    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder': '', 'autocomplete': 'current-password'}),
    )
