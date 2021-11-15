from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from .models import CustomUser
from listings.models import Product
from .models import Profile
from django.forms import ModelForm, TextInput, EmailInput

# Register your models here.

class UserCreationForm(forms.ModelForm):
    """
    A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder':'', 'class': 'input-field',}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'placeholder':'', 'class': 'input-field',}))
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'placeholder':'', 'class': 'input-field',}))

    class Meta:
        model = CustomUser
        # Enter the required fields for your custom user
        fields = ('email',)
    
    def clean_password2(self):
        # checks that both passwords entries are equal on the form

        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        # checks to see if both passwords are True and if they are not equal
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format

        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    A form for updating users in the admin page. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'is_admin',)
    

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # List display holds the field names of the fields that we want 
    # to display on our admin account page of our users.
    list_display = ('email',)

    # List filter choses what filter options to display on the filter panel on the right hand side of the admin page.
    list_filter = ('is_admin',)

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    fieldsets = (
        ('User Info', {'fields': ('email', 'password',)}),
        ('Permissions', {'fields': ('is_admin',)})
        )

    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
      

    # add_fieldsets is used to define the fields that will be displayed on the create user page

    # The classes key sets any custom CSS classes we want ot apply on our form section.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2',)
        }),
        ('Permissions', {'fields': ('is_admin', 'is_superuser',)})
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

class ListingsAdmin(admin.ModelAdmin):

    list_display = ('author','name', 'price', 'date_added',)

    list_filter = ('author',)

    search_fields = ('author',)
    ordering = ('author',)
    filter_horizontal = ()


admin.site.register(CustomUser, UserAdmin)

admin.site.register(Profile)
admin.site.register(Product, ListingsAdmin)

    
    


