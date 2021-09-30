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
    path('register/', account.register, name="register-page"),

    path('login/', 
            account.UserLoginView.as_view(template_name="account/login.html"), 
                name="login-page"),

    path('logout/', 
            auth_views.LogoutView.as_view(template_name="account/logout.html"), 
                name="logout-page"),

    # Initial password reset form
    path('password-reset/', 
            auth_views.PasswordResetView.as_view(template_name="account/password_reset.html"), 
                name="password-reset-page"),
    

    # Email is sent at this point.
    path('password-reset/done/', 
            auth_views.PasswordResetDoneView.as_view(template_name="account/password_reset_done.html"), 
                name="password_reset_done"),


    # This url path is path that the email links to.
    path('password-reset/confirm/<uidb64>/<token>/', 
            auth_views.PasswordResetConfirmView.as_view(template_name="account/password_reset_confirm.html"), 
                name="password_reset_confirm"),

    # Connection refused error will b encountered during this process.
    # To circumvent this, an email service must be set up.
    # Gmail is a great option but there are many other services as well, I've heard.
    # To setup a localhost server instead(not the best approach), use this 
    # https://docs.djangoproject.com/en/2.1/topics/email/#configuring-email-for-development

    # Notifies the user that an email has been sent. 
    path('password-reset/complete/', 
            auth_views.PasswordResetCompleteView.as_view(template_name="account/password_reset_complete.html"), 
                name="password_reset_complete"),

    path('profile/', account.profile, name="profile-page"),
    path('listings/', include('listings.urls')),
    path('forbidden/', account.forbidden_space, name="login-required"),
    path('', include('layout.urls')),
]

# Needed to be able to serve images - NOT safe for production
if settings.DEBUG == True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


