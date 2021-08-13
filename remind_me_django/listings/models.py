from django.db import models
from django.conf import settings

# Create your models here.

class Product(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=20, blank=True)
    price = models.FloatField()
    stock = models.BooleanField()
    url = models.URLField(max_length=2000)
    quantity = models.CharField(max_length=30, null=True)

    def __str__(self):
        return self.url


