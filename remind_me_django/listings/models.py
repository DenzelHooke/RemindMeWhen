from django.db import models
from django.conf import settings

# Create your models here.

class Product(models.Model):
    url = models.URLField(max_length=2000)
    price = models.FloatField()
    stock = models.BooleanField()
    quantity = models.CharField(max_length=30)
    # on user account deletion, delete all of their product listings. 
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


