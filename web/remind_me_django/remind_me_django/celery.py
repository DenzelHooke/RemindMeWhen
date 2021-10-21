import os
from datetime import datetime as dt
import pytz

import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'remind_me_django.settings'
django.setup()

from listings.models import Product
from celery import Celery
from .task_funcs import ScraperUtilz

scrapyd_api = 'http://scrapy:8080'

app = Celery('remind_me_django')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks.py modules from all registered Django apps.
app.autodiscover_tasks()

# 'on_after_configure' is a signal to be sent after the celery app instance has *prepared* it's config settings.
@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(60, check_for_updates.s(), name='check DB every 10')


@app.task
def check_for_updates():
    # Can't compare offset aware(dt with timezone) with offset naive(dt without a timezone) datetime objects so 
    # we localize our current time into a offset aware dt object.
    utc_now = pytz.utc.localize(dt.utcnow())
    all_products = Product.objects.all()
    for product in all_products:
        diff = utc_now - product.last_updated
        product.last_checked = utc_now
        if diff.total_seconds() / 60 >= 30:
            print(f'db_periodic_checker: Product: {product.name[:20]}.. To be updated.\nLast checked: {diff.total_seconds() / 60} minutes ago')

            print(product.url)
            scraper = ScraperUtilz(scrapyd_api)
            scraper.scrapyd_update_run(product.author, product)
            scraper.wait_till_finished(1)

            # Store scrapped data in Redis with a uuid as a JSON str
            # Pull down data with that specified uuid
            # Compare prices with curent prices in databse
            # if differrent, save old price in a var, update db with new dtaa and send an email showing the price comparisons.
            # Create a class for this

            print(f'db_periodic_checker: Product: {product.name[:20]}.. updated')
        else:
            print(f'db_periodic_checker: Product: {product.name[:20]}.. skipped.\nLast checked: {diff.total_seconds() / 60} minutes ago')
        
                 
        
    # If products differ from scraped resuslts add them onto Product
    # If compared price is different, change price in DB and send an email informing the user that price has changed.
    
    


