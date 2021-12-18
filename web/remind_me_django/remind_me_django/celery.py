import os
import time
from datetime import datetime as dt, timedelta
import pytz
import json
import logging
from random import randrange


import redis
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'remind_me_django.settings'
django.setup()
from django.core.mail import send_mail
from listings.models import Product
from celery import Celery
from .task_funcs import ScraperUtilz, update_prod_last_updated, scrape_https_proxies
from .email_stuff import Product_Email



r = redis.Redis(host='redis', port=6379, db=0)
scrapyd_api_url = 'http://scrapy:8080'
app = Celery('remind_me_django')

# 5 min
time_to_run = 300
minute_to_check = 10
# time_to_check = timedelta(minutes=5).total_seconds


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load tasks.py modules from all registered Django apps.
app.autodiscover_tasks()

# 'on_after_configure' is a signal to be sent after the celery app instance has *prepared* it's config settings.
try:
    @app.on_after_configure.connect
    def setup_periodic_tasks(sender, **kwargs):
        # sender.add_periodic_task(time_to_run, check_for_updates.s(), name='check DB every X')
        sender.add_periodic_task(timedelta(minutes=5), scrape_proxies.s(), name='scrape_free_proxies')

except ConnectionError("Connection Error on elephant SQL, slow down celery task!"):
    print("SQL ELEPHANT Connection Error")


@app.task
def check_for_updates():
    """
    Peridocally runs scrapyd processes to check if product page data has been updated
    """

    # Can't compare offset aware(dt with timezone) with offset naive(dt without a timezone) datetime objects so 
    # we localize our current time into a offset aware dt object.

    all_products = Product.objects.all()
    utc_now = pytz.utc.localize(dt.utcnow())
    db_error_count_limit = 3
    count = 0   
    # 10 min
    db_slowdown_ttl = 300

    if r.get('check_DB_slowdown'):
        print('Amazon Throttle detected, skipping on checking products')

    else:
        for product in all_products:
            author = product.author
            diff = utc_now - product.last_updated
            
            # If the product was last checked past a certain time, send it to the scraper
            try: 
                if diff.total_seconds() / 60 >= minute_to_check:
                    print(f'db_periodic_checker: Product: {product.name[:20]} Last checked: {diff.total_seconds() / 60} minutes ago.')
                    scraper = ScraperUtilz()
                    time.sleep(randrange(3, 8))
                    
                    # Check if the db count is greater than X
                    if r.get("check_DB_error_count"):
                        print('')
                        # If the key exists and it's count is greater or equal to the limit, 
                        # Create a key with the desired ttl.
                        # This is the slowdown key and will put a temp hold on any changes to product data, including this celery task.

                        if int(r.get("check_DB_error_count")) >= db_error_count_limit:
                            count = 0
                            utc_now = pytz.utc.localize(dt.utcnow())

                            r.set("check_DB_slowdown", str(utc_now))
                            r.expire("check_DB_slowdown", db_slowdown_ttl)
                            break

                    try:
                        scraper.scrapyd_update_run(author, product)
                        scraper.wait_till_finished(1)
                        new_product_data = json.loads(r.get(scraper.uuid))
                    except Exception as e:
                        print(e)
                        print("Product Skipped due to the scraper not finding the product page")
                        print(product)
                        count += 1
                        print(f"Error count: {count}")
                        r.set("check_DB_error_count", count)
                        if r.ttl("check_DB_error_count") < 0:
                            r.expire("check_DB_error_count", 20)
                        continue

                    current_time = pytz.utc.localize(dt.utcnow())
                    new_prod_price = new_product_data['price']
                    old_prod_price = product.price
                    product_email = Product_Email(product, new_product_data)
                    
                    # If new_price doesn't match up with current price and it's in stock
                    if new_prod_price != old_prod_price and new_product_data['stock']:
                        
                        # Updated current product price with new price
                        product.price = new_prod_price
                        product.last_updated = current_time
                        product.save()

                        # Calculate price difference
                        price_diff = product_email.price_diff

                        if price_diff > 0:
                            # new prod price has decreased
                            if not product.stock:
                                # If the product is currently out of stock, send an in stock & price decrease email
                                product_email.send_in_stock_price_decrease()
                            else:
                                # If it was already in stock, just send a price decreease email
                                product_email.send_price_decrease_email()
                                print(f'db_periodic_checker: Product: "{product.name[:20]}" updated')
                                print(f'db_periodic_checker: Email sent to "{product.author.email}"')

                        elif price_diff < 0:
                            # price has increased

                            if not old_prod_price:
                                # If there is no
                                product_email.send_in_stock_email()
                        
                            # product_email.send_price_increase_email()
                            # print(f'db_periodic_checker: Product: "{product.name[:20]}" updated')
                            # print(f'db_periodic_checker: Email sent to "{product.author.email}"')

                    elif new_prod_price != old_prod_price and not new_product_data['stock']:
                        # If current product was out of stock before the scrape then the product price is only updated.

                        # # Prod is unavailable
                        # if new_prod_price == 0:
                        #     product_email.send_out_of_stock_email()
                            
                        product.price = new_product_data['price']

                        # Else if product was in stock before the scrape but it's now out of stock.
                        if product.stock:
                            product_email.send_out_of_stock_email()
                    
                        product.stock = False
                        update_prod_last_updated(product, current_time)
        
                    #  If not in stock
                    elif not new_product_data['stock']:
                        #If the scrapped product was already out of stock, do nothing
                        if not product.stock:
                            pass
                        else:
                            product.stock = new_product_data['stock']
                            product_email.send_out_of_stock_email()
                            update_prod_last_updated(product, current_time)
                    
                    # If in stock
                    elif new_product_data['stock']:
                        #If the scrapped product was already in stock, do nothing
                        if product.stock:
                            pass
                        else:
                            product.stock = new_product_data['stock']
                            product_email.send_in_stock_email()
                            update_prod_last_updated(product, current_time)


                    utc_now_last_checked = pytz.utc.localize(dt.utcnow())
                    product.last_checked = utc_now_last_checked
                    product.save()
                    time.sleep(5)

                else:
                    print(f'db_periodic_checker: Product: {product.name[:20]}.. skipped.\nLast checked: {diff.total_seconds() / 60} minutes ago')
            except Exception as e:
                print(e)
            

@app.task
def scrape_proxies():
    logging.debug("scraping proxies.")
    proxies_list = [
        'https://free-proxy-list.net/',
        ]

    # Store proxies in Redis.
    good_proxies = scrape_https_proxies(proxies_list)
    logging.debug(good_proxies)
    
    if r.lrange('https_proxies', 0, -1):
        logging.debug("Proxy array already exists with Redis DB, deleting array.")   
        r.delete('https_proxies')
    r.lpush('https_proxies', *good_proxies)
