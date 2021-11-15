import time

import json
import redis
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, DeleteView
from .models import Product
from .forms import ProductCreationForm
from remind_me_django.task_funcs import ScraperUtilz




r = redis.Redis(host='redis', port=6379, db=0)


@login_required
def listing_add(request):
    """ 
    Creates a form for adding a product to track.
    Once form is valid, the product object is returned(not saved into DB) and
    the scrapyd_run is called and passed both request and product objects.
    """
    user = request.user
    context = {}

    if request.method == "POST":
        product_form = ProductCreationForm(request.POST)
        if product_form.is_valid():
            print(f"---{user}---")

            # Runs the code that spawns a scrapyd process.
            scraper = ScraperUtilz()
            scraper.scrapyd_first_run(request, product_form.save(commit=False))
            scraper.wait_till_finished(1)

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

    else:
        product_form = ProductCreationForm()
        template = "listings/listing_landing.html"
        
    context['sidebar'] = True
    context['form'] = product_form
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

    