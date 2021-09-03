from django import forms
from django.forms import ModelForm, TextInput, EmailInput
from django.forms.widgets import URLInput
from .models import Product



class ProductCreationForm(forms.ModelForm):
    
    class Meta:
        model = Product
        # Tells our form that we want to work with the email fields
        fields = ['name', 'url']

        widgets = {
            'name': TextInput(attrs={'placeholder':'Optional product name', 'class':"input-field"}
            ),
            'url': URLInput(attrs={'placeholder':'Enter an Amazon.com or Amazon.ca URL', 'class':"input-field"}
            )
        }






