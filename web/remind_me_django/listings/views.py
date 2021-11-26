import time

import json
import redis
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


r = redis.Redis(host='redis', port=6379, db=0)

def slowdown_detected(slowdown, request):
    slowdown = slowdown.decode("utf-8")
    slowdown_date = parser.parse(slowdown)
    utc_now = pytz.utc.localize(dt.utcnow())
    print(slowdown)
    time_until_avail = utc_now - slowdown_date  
    time_until_avail = 600 - time_until_avail.total_seconds()

    # Means amazon has temp throttled our IP and we must wait before we can scrape again
    print("Scraper is currently being throttled by Amazon")
    #send flash message informing user
    messages.warning(request, f"Our Amazon scraper is temporarily unavailable, please try again shortly in {int(time_until_avail)} seconds")

def user_slowdown_detected(slowdown, request, initial_ttl):
    slowdown = slowdown.decode("utf-8")
    slowdown_date = parser.parse(slowdown)
    utc_now = pytz.utc.localize(dt.utcnow())
    print(slowdown)
    time_until_avail = utc_now - slowdown_date
    time_until_avail = initial_ttl - time_until_avail.total_seconds()


    print(f"user: {request.user} is on a temp slowdown")
    #send flash message informing user
    if initial_ttl > 60:
        # convert to minutes
        initial_ttl = initial_ttl / 60
        messages.warning(request, f"Please try again shortly in {int(initial_ttl)} minutes.")
    else:
        messages.warning(request, f"Please try again shortly in {int(time_until_avail)} seconds.")


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


        
    if request.method == "POST" and not r.get(f"TEMP-USER-BLOCK:{user.email}"):
        print("POST MADE")
        product_form = ProductCreationForm(request.POST)
        if product_form.is_valid():
            print(f"---{user}---")
            check_DB_slowdown = r.get("check_DB_slowdown")
            print(f'----celery_slowdown: {check_DB_slowdown}----')
            if check_DB_slowdown:
                slowdown_detected(check_DB_slowdown, request)
                return redirect('listing-add-page')

            else:
                # Check if user is blocked from making scrapes
                
                user_slowdown_count = r.get(f"MANUAL_SCRAPE_ERROR_COUNT-{user.email}")
                if user_slowdown_count and int(user_slowdown_count) >= error_count_limit:
                    print("BING_____")
                    utc_now = pytz.utc.localize(dt.utcnow())
                    if not r.get(f"TEMP-USER-BLOCK:{user.email}"):
                        r.setex(f"TEMP-USER-BLOCK:{user.email}", temp_ban_key_ttl, str(utc_now))

                else:
                    print("--scraper add view--")
                    # Runs the code that spawns a scrapyd process.
                    scraper = ScraperUtilz()
                    scraper.scrapyd_first_run(request, product_form.save(commit=False))
                    scraper.wait_till_finished(1)
                    try:
                        prod = json.loads(r.get(scraper.uuid))
                        Product.objects.create(
                            author=user,
                            name=prod['name'],
                            price=prod['price'],
                            stock=prod['stock'],
                            url=prod['url']
                        )

                        newest_listing = Product.objects.filter(author=user).latest('date_added')

                        # Renders the detail view 
                        return redirect('listing-detail', pk=newest_listing.pk)
                    except:
                        utc_now = pytz.utc.localize(dt.utcnow())
                        user_error_count = r.get(f"MANUAL_SCRAPE_ERROR_COUNT-{user.email}")
                        print(user_error_count)
                        if not user_error_count:
                            print("user error count SET")

                            r.setex(f"MANUAL_SCRAPE_ERROR_COUNT-{user.email}", 
                            temp_ban_count_ttl, 
                            1)
                        else:
                            print("user error count ADDED")
                            count_ttl = r.ttl(f"MANUAL_SCRAPE_ERROR_COUNT-{user.email}")

                            r.setex(f"MANUAL_SCRAPE_ERROR_COUNT-{user.email}",
                            count_ttl,
                            int(user_error_count)+1)

                        messages.warning(request, f"Sorry, that Amazon page couldn't be found at this time.")
    
    product_form = ProductCreationForm()
    template = "listings/listing_landing.html"
    
    context['sidebar'] = True
    context['form'] = product_form

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

    