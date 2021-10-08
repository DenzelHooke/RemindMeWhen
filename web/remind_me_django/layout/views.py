from django.shortcuts import render
from django.contrib.auth import views as auth_views

# Create your views here.

def home_page(request):
    return render(request, 'layout/index.html')