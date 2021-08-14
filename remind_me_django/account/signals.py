from django.db.models.signals import post_save
# Post save runs when a model runs it's save() method aka when a user object is created in our case

from .models import CustomUser
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)





