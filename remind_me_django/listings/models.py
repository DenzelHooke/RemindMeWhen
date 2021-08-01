from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Product(models.Model):
    url = models.CharField(max_length=400)
    price = models.FloatField()
    stock = models.BooleanField()
    quantity = models.CharField(max_length=30)
    # on user account deletion, delete all of their product listings. 
    author = models.ForeignKey(User, on_delete=models.CASCADE)

