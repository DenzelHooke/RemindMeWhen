import django
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'remind_me_django.settings'
import time
from scrapyd_api import ScrapydAPI
from models import Product
django.setup()


def delete_project():
    scrapyd = ScrapydAPI('http://localhost:8080')
    print(scrapyd.list_projects())


def to_default(profile):
    if os.path.exists(profile.image.path):
        print(f"{profile} Image contains an image.")
    else:
        profile.image = "default.jpg"
        profile.save()
        print(f"{profile} Image default added!")


# for profile in Profile.objects.all():
#     to_default(profile)

for product in Product.objects.all():
    product.name = 'code'
    product.save()
    time.sleep(1)