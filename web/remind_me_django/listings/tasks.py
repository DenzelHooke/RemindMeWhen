import json
import os

import pytz
from datetime import datetime as dt, timedelta
import redis
import logging
from decouple import config
from account.models import CustomUser
from listings.models import Product
from celery import shared_task, Celery
from remind_me_django.task_funcs import  ScraperUtilz
from remind_me_django.settings import REDIS_HOST, REDIS_PORT, REDIS_PASS

# Create your tasks here

pool = redis.ConnectionPool(
    host=REDIS_HOST, 
    password=REDIS_PASS, 
    port=REDIS_PORT,  
    db=0
    )
r = redis.Redis(connection_pool=pool)

def manage_temp_ban(user, temp_ban_count_ttl):
    """Creates or incrmenets a temp ban for the user. 

    Args:
        user (user object): Django lazy user object.
        temp_ban_count_ttl (int): An int that represents the amount of time a temp ban should last.
    """
    utc_now = pytz.utc.localize(dt.utcnow())
    user_error_count = r.get(f"MANUAL_SCRAPE_ERROR_COUNT-{user}")
    logging.debug(user_error_count)
    if not user_error_count:
        # If not, create a key with a value of 1 (initial error)
        logging.debug("user error count SET")

        r.setex(
        f"MANUAL_SCRAPE_ERROR_COUNT-{user}", 
        temp_ban_count_ttl, 
        1)
    else:
        # If it already exists, get the current ttl, create a new key with the old key's ttl but increment the error count by 1

        logging.debug("user error count ADDED")
        count_ttl = r.ttl(f"MANUAL_SCRAPE_ERROR_COUNT-{user}")
        if count_ttl:
            r.setex(
            f"MANUAL_SCRAPE_ERROR_COUNT-{user}",
            count_ttl,
            int(user_error_count)+1)

@shared_task
def create_product(user_email, product_form, temp_ban_count_ttl):
    """Creates a product row.

    Args:
        user (user object): Django lazy user object.
        scraper (object): A scraper object instance.
    """
    scraper = ScraperUtilz(state='production')

    print('bg task ran')
    scraper.scrapinghub_first_run(user_email, product_form)
    # Polls until job is finished or if it fails.
    scraper.wait_till_finished(state="production")
    try: 
        prod = json.loads(r.get(scraper.uuid))
        Product.objects.create(
            author=CustomUser.objects.filter(email=user_email).first(),
            name=prod['name'],
            price=prod['price'],
            stock=prod['stock'],
            url=prod['url']
        )
    except TypeError:
        manage_temp_ban(user_email, temp_ban_count_ttl)
