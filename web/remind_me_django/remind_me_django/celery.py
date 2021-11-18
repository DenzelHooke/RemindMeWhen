import os
import time
from datetime import datetime as dt, timedelta
import pytz
import json
import redis

import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'remind_me_django.settings'
django.setup()
from django.core.mail import send_mail
from listings.models import Product
from celery import Celery
from .task_funcs import ScraperUtilz











r = redis.Redis(host='redis', port=6379, db=0)
scrapyd_api_url = 'http://scrapy:8080'
app = Celery('remind_me_django')
time_to_check = timedelta(minutes=5)


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
    sender.add_periodic_task(time_to_check, check_for_updates.s(), name='check DB every 10')


@app.task
def check_for_updates():
    """Peridocally runs scrapyd processes to check if..
    """

    # Can't compare offset aware(dt with timezone) with offset naive(dt without a timezone) datetime objects so 
    # we localize our current time into a offset aware dt object.
    all_products = Product.objects.all()
    utc_now = pytz.utc.localize(dt.utcnow())

    for product in all_products:
        author = product.author

        diff = utc_now - product.last_updated
        if diff.total_seconds() / 60 >= time_to_check.seconds:
            print(f'db_periodic_checker: Product: {product.name[:20]} Last checked: {diff.total_seconds() / 60} minutes ago.')
            current_time = pytz.utc.localize(dt.utcnow())
            scraper = ScraperUtilz()
            # Attatch an uuid to the scrapy product and store that in redis
            scraper.scrapyd_update_run(author, product)
            scraper.wait_till_finished(1)

            prod = r.get(scraper.uuid)
            prod = json.loads(prod)

            # Throws error here if amazon page doesn't have a price
            new_prod_price = prod['price']
            current_prod_price = product.price
            
            if new_prod_price != current_prod_price and prod['stock']:

                product.price = new_prod_price
                product.last_updated = current_time
                product.save()

                price_diff = current_prod_price - new_prod_price
                if price_diff > 0:
                    # new prod price has decreased
                    
                    send_mail(
                        'RemindMeWhen Price Alert!',
                        f"""
                        Hello, your product "{product.name}" has decreased in price by ${price_diff}!

                                Old price: {current_prod_price} || Updated price: {product.price}            


                        Here is your product page: {product.url}
                        """,
                        'denzelthecreator@gmail.com',
                        [product.author.email],
                        fail_silently=False,
                    )

                    print(f'db_periodic_checker: Product: "{product.name[:20]}" updated')
                    print(f'db_periodic_checker: Email sent to "{product.author.email}"')

                elif price_diff < 0:
                    # price has increased

                    # convert to a postive difference
                    positive_diff = price_diff * -1

                    # product.price = new_prod_price
                    
                    send_mail(
                        'RemindMeWhen Price Alert!',
                        f"""
                        Hello, your product "{product.name}" has increased in price by ${"%.2f" % positive_diff}!

                        |------------------------------------------------------------------|
                        |Old price: {current_prod_price} || Updated price: {product.price}|
                        |------------------------------------------------------------------|


                        Here is your product page: {product.url}
                        """,
                        'denzelthecreator@gmail.com',
                        [product.author.email],
                        fail_silently=False,
                    )
                    
                    print(f'db_periodic_checker: Product: "{product.name[:20]}" updated')
                    print(f'db_periodic_checker: Email sent to "{product.author.email}"')

            elif not prod['stock']:
                product.stock = prod['stock']
                product.price = 0
                product.last_updated = current_time
                product.save()
            else:
                # don't run a DB operation since prices haven't changed
                pass

            product.last_checked = utc_now
            product.save()
            time.sleep(5)

        else:
            print(f'db_periodic_checker: Product: {product.name[:20]}.. skipped.\nLast checked: {diff.total_seconds() / 60} minutes ago')
        
                 
        
    # If products differ from scraped resuslts add them onto Product
    # If compared price is different, change price in DB and send an email informing the user that price has changed.
    
    


