from django.db.models.signals import post_save
# Post save runs when a model runs it's save() method aka when a user object is created in our case

from .models import CustomUser
from django.dispatch import receiver
from .models import Profile

# receiver takes a signal and a model to look at. 
# post_save is our signal
# post_save gets tripped after our CustomUser runs it's save() method which happens when a new model is created. 

# our signal passes in sender, instance, created and other kwargs to our decorator function
# Created gets set to True, if an instance was created of our sender model
# if it was, we then create a profile and pass in the user field as the current user instance that was just created. 

# objects.create() creates he instance and saves automatically.
@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)





