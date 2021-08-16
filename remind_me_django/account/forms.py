from django import forms
from .models import CustomUser, Profile

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        # Tells our form that we want to work with the email fields
        fields = ['email']

class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ['image', 'bio']
