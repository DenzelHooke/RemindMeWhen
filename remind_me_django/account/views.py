from django.shortcuts import render, redirect
from account.admin import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm


# Create your views here.
def register(request):

    if request.method == 'POST':
        # if post request is sent back, create a form with the post data
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            messages.success(request, f"Account created for '{email}'")
            return redirect('login-page')
    else:
        form = UserCreationForm()
    title = 'Register'
    return render(request, 'account/register.html', {'form': form, 'title': title})

# Message Types

# messages.debug
# messages.info
# messages.warning
# messages.success
# messages.error



@login_required
def profile(request):
    
    if request.method == "POST":
            # request.POST sends our post data to the form
            # instance tells the form which instance of that model to update
            # request.user is the currently logged in user

        userForm = UserUpdateForm(request.POST, instance=request.user)
        profileForm = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)    
        
        if userForm.is_valid() and profileForm.is_valid():
            userForm.save()
            profileForm.save()
            

            shorthand_name = request.user.get_name()
            messages.success(request, f"Your account has been updated, {shorthand_name}")
            # redirect ends the post/get request pattern which happens when you try to refresh the page after sending a post request and you get thta pop up hta says you'll resend form information if you refresh. 
            return redirect('profile-page')


    else:
        # Puts our curent user data in each form
        userForm = UserUpdateForm(instance=request.user)
        profileForm = ProfileUpdateForm(instance=request.user.profile)
        

    context = {'user_form': userForm, 'profile_form': profileForm}

    return render(request, "account/profile.html", context=context)



def forbidden_space(request):
    return render(request, "account/login_required.html")

