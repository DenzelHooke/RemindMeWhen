from django.db import models
from django.conf import settings
from django.urls import reverse

# Create your models here.

class Product(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="product")
    name = models.CharField(max_length=50, blank=True)
    price = models.FloatField()
    stock = models.BooleanField()
    url = models.URLField(max_length=2000)
    quantity = models.CharField(max_length=30, blank=True, default="None")
    date_added = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["date_added"]

    def __str__(self):
        return f"{self.url[:40]}.." 

    def get_absolute_url(self):
        # Reverse returns the full URL path to the specified url path name.
        # When using create class based views, after creating ias succesful, it tries to redirect you to the detail view of the object that was just created. Here we pass it the location of the url path and the primary key of the object.
        return reverse('listing-detail', kwargs={'pk': self.id})




