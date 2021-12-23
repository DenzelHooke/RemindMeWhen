import time
import logging


import json
import redis
from decouple import config
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, DeleteView
from .models import Product
from .forms import ProductCreationForm
from remind_me_django.task_funcs import ScraperUtilz
import pytz
from datetime import datetime as dt, timedelta
from dateutil import parser


logging.basicConfig(level=logging.DEBUG)
r = redis.Redis(
    host=config('REDIS_HOST'), 
    password=config('REDIS_PASS'), 
    port=config('REDIS_PORT'), 
    db=0)

def slowdown_detected(slowdown, request):
    """Runs if a slowdown is detected from the celery auto updater.
    Displays an error message to the user.

    Args:
        slowdown (Redis byte): A redis byte object that represents the datetime when the slowdown was set.
        request (request object): Django request object.
    """
    slowdown = slowdown.decode("utf-8")
    slowdown_date = parser.parse(slowdown)
    utc_now = pytz.utc.localize(dt.utcnow())
    logging.debug(slowdown)
    time_until_avail = utc_now - slowdown_date  
    time_until_avail = 600 - time_until_avail.total_seconds()

    # Means amazon has temp throttled our IP and we must wait before we can scrape again
    logging.critical("Scraper is currently being throttled by Amazon")
    #send flash message informing user
    messages.warning(request, f"Our Amazon scraper is temporarily unavailable, please try again shortly in {int(time_until_avail)} seconds")

def user_slowdown_detected(slowdown, request, initial_ttl):
    """Runs if user has a temp ban. Displays an error message to the user.

    Args:
        slowdown (Redis byte): A redis byte object that represents the datetime when the slowdown was set.
        request (request object): Django request object.
        initial_ttl (The current ttl of the Redis object): The current ttl of the temp ban.
    """
    slowdown = slowdown.decode("utf-8")
    slowdown_date = parser.parse(slowdown)
    utc_now = pytz.utc.localize(dt.utcnow())
    logging.debug(slowdown)
    time_until_avail = utc_now - slowdown_date
    time_until_avail = initial_ttl - time_until_avail.total_seconds()


    logging.warning(f"user: {request.user} is on a temp slowdown")
    #send flash message informing user
    if initial_ttl > 60:
        # convert to minutes
        initial_ttl = initial_ttl / 60
        messages.warning(request, f"Please try again shortly in {int(initial_ttl)} minutes.")
    else:
        messages.warning(request, f"Please try again shortly in {int(time_until_avail)} seconds.")

def create_product(user, scraper):
    """Creates a product row.

    Args:
        user (user object): Django lazy user object.
        scraper (object): A scraper object instance.
    """
    prod = json.loads(r.get(scraper.uuid))
    Product.objects.create(
        author=user,
        name=prod['name'],
        price=prod['price'],
        stock=prod['stock'],
        url=prod['url']
    )

def manage_temp_ban(user, temp_ban_count_ttl):
    """Creates or incrmenets a temp ban for the user. 

    Args:
        user (user object): Django lazy user object.
        temp_ban_count_ttl (int): An int that represents the amount of time a temp ban should last.
    """
    utc_now = pytz.utc.localize(dt.utcnow())
    user_error_count = r.get(f"MANUAL_SCRAPE_ERROR_COUNT-{user.email}")
    logging.debug(user_error_count)
    if not user_error_count:
        # If not, create a key with a value of 1 (initial error)
        logging.debug("user error count SET")

        r.setex(
        f"MANUAL_SCRAPE_ERROR_COUNT-{user.email}", 
        temp_ban_count_ttl, 
        1)
    else:
        # If it already exists, get the current ttl, create a new key with the old key's ttl but increment the error count by 1

        logging.debug("user error count ADDED")
        count_ttl = r.ttl(f"MANUAL_SCRAPE_ERROR_COUNT-{user.email}")
        if count_ttl:
            r.setex(
            f"MANUAL_SCRAPE_ERROR_COUNT-{user.email}",
            count_ttl,
            int(user_error_count)+1)



@login_required
def listing_add(request):
    """ 
    Creates a form for adding a product to track.
    Once form is valid, the product object is returned(not saved into DB) and
    the scrapyd_run is called and passed both request and product objects.
    """
    user = request.user
    context = {}
    temp_ban_key_ttl = 60
    temp_ban_count_ttl = 60
    error_count_limit = 3


    # If there is a post request but not a temp block for the user issuing the post request 
    if request.method == "POST" and not r.get(f"TEMP-USER-BLOCK:{user.email}"):
        logging.debug("POST MADE")
        product_form = ProductCreationForm(request.POST)
        if product_form.is_valid():
            logging.debug(f"---{user}---")
            check_DB_slowdown = r.get("check_DB_slowdown")
            logging.debug(f'----celery_slowdown: {check_DB_slowdown}----')
            if check_DB_slowdown:
                # If a db slowdown exists, display a message to the user and redirect them. 
                slowdown_detected(check_DB_slowdown, request)
                return redirect('listing-add-page')

            else:
                # Check if user has exceeded the error limit
                
                # If user slowdown exists and it's count is greater than the error count limit
                user_slowdown_count = r.get(f"MANUAL_SCRAPE_ERROR_COUNT-{user.email}")
                if user_slowdown_count and int(user_slowdown_count) >= error_count_limit:
                    logging.debug("BING_____")
                    utc_now = pytz.utc.localize(dt.utcnow())
                    # If the user doesn't already have a temp block already set, create one.
                    if not r.get(f"TEMP-USER-BLOCK:{user.email}"):
                        r.setex(f"TEMP-USER-BLOCK:{user.email}", temp_ban_key_ttl, str(utc_now))

                else:
                    logging.debug("--scraper add view--")
                    # Runs the code that spawns a scrapyd process.
                    scraper = ScraperUtilz()
                    scraper.scrapyd_first_run(request, product_form.save(commit=False))
                    scraper.wait_till_finished(1)
                    try:
                        create_product(user, scraper)
                        newest_listing = Product.objects.filter(author=user).latest('date_added')

                        # Renders the detail view 
                        return redirect('listing-detail', pk=newest_listing.pk)
                    except TypeError:
                        # There was most likely a key error (Redis key wasn't created due to page not being found)
                        manage_temp_ban(user, temp_ban_count_ttl)
                        messages.warning(request, f"Sorry, that Amazon page couldn't be found at this time.")
    
    product_form = ProductCreationForm()
    template = "listings/listing_landing.html"
    
    context['sidebar'] = True
    context['form'] = product_form

    # If t
    if r.get(f"TEMP-USER-BLOCK:{user.email}"):
        context['temp_user_block'] = True
        user_slowdown_detected(r.get(f"TEMP-USER-BLOCK:{user.email}"), request, temp_ban_key_ttl)
    else:
        context['temp_user_block'] = False

    return render(request, template, context)


class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name="listings/listing_home.html" # Default path if temp_name isn't created: <app>/<model>_<viewtype>.html

    ordering = ['date_added']
    paginate_by = 5

    def get_queryset(self, *args,  **kwargs):
        queryset = Product.objects.filter(author=self.request.user)
        
        # print(queryset)
        return queryset
    
    def get_context_data(self, *args,  **kwargs):
        context = super().get_context_data(*args,  **kwargs)
        context['sidebar'] = True
        # print(context)
        return context

class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    success_url = '/listings'

    def test_func(self):
        # self.get_object() returns the instance of the object trying to be 
        # accessed based off of the pk sent into the view
        product = self.get_object()
        # Check if user who sent request is the author of that object
        if self.request.user == product.author:
            return True
        else:
            return False

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "listings/product_detail.html"
    context_object_name = "product"

    