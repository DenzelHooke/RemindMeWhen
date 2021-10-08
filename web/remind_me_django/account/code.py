import os
from scrapyd_api import ScrapydAPI
os.environ['DJANGO_SETTINGS_MODULE'] = 'remind_me_django.settings'


def delete_project():
    scrapyd = ScrapydAPI('http://localhost:8080')
    print(scrapyd.list_projects())

delete_project()


def to_default(profile):
    if os.path.exists(profile.image.path):
        print(f"{profile} Image contains an image.")
    else:
        profile.image = "default.jpg"
        profile.save()
        print(f"{profile} Image default added!")


# for profile in Profile.objects.all():
#     to_default(profile)