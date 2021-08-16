import os
import models


def to_default(profile):
    if os.path.exists(profile.image.path):
        print(f"{profile} Image contains an image.")
    else:
        profile.image = "default.jpg"
        profile.save()
        print(f"{profile} Image default added!")


for profile in Profile.objects.all():
    to_default(profile)