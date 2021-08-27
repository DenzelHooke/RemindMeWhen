# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import sys
sys.path.append("C:\\Users\\Denze\\Projects\\remindMe\\remind_me_django")

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'remind_me_django.settings'

# Needed to get access to django files
import django
django.setup()


from scrapy_djangoitem import DjangoItem
from listings.models import Product


class ProductItem(DjangoItem):
    # define the fields for your item here like:
    django_model = Product
    
