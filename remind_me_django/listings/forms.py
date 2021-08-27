from django import forms
from .models import Product



class ProductCreationForm(forms.ModelForm):

    class Meta:
        model = Product
        # Tells our form that we want to work with the email fields
        fields = ['name', 'url']






