from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.conf import settings

# https://docs.djangoproject.com/en/3.2/ref/models/fields/


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """

        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(email=self.normalize_email(email))

        user.set_password(password)
        user.save(using=self._db)
        print("--user created--")

        return user
    
    def create_superuser(self, email, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """

        user = self.create_user(email, password=password)

        user.is_admin = True
        user.save(using=self._db)
        print("--superuser created--")

        return user








class CustomUser(AbstractBaseUser):
    email = models.EmailField(verbose_name='email', max_length=80,  unique=True)

    USERNAME_FIELD = 'email'


    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    date_joined = models.DateField(auto_now_add=True)
    
    
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True
    
    def get_name(self):
        return self.email.split('@')[0]

    @property
    def is_staff(self): 
        return self.is_admin
        


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    image = models.ImageField(default="default.jpg", upload_to='profile_pics')
    bio = models.TextField(blank=True)


    def __str__(self):
        return self.user.email.split("@")[0]