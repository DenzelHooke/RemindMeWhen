"""remind_me_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from account import views as account
from listings import views as listings
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('layout.urls')),
    path('register/', account.register, name="register-page"),
    path('login/', auth_views.LoginView.as_view(template_name="account/login.html"), name="login-page"),
    path('logout/', auth_views.LogoutView.as_view(template_name="account/logout.html"), name="logout-page"),
    path('profile/', account.profile, name="profile-page"),
    path('listings/', include('listings.urls')),
    path('forbidden/', account.forbidden_space, name="login-required"),
]

# Needed to be able to serve images - NOT safe for production
if settings.DEBUG == True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


