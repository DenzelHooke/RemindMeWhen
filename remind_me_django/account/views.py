from django.shortcuts import render, redirect
from account.admin import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Create your views here.
def register(request):

    if request.method == 'POST':
        # if post request is sent back, create a form with the post data
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            messages.success(request, f"Account created for '{email}'")
            return redirect('home-page')
    else:
        form = UserCreationForm()
    title = 'Register'
    return render(request, 'account/register.html', {'form': form, 'title': title})

@login_required
def profile(request):
    return render(request, "account/profile.html")

def forbidden_space(request):
    return render(request, "account/login_required.html")


# Message Types

# messages.debug
# messages.info
# messages.warning
# messages.success
# messages.error