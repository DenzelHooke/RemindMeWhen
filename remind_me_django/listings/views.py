import operator
import sys
sys.path.append("C:\\Users\\Denze\\Projects\\remindMe\\remind_me_scraper\\remind_me_scraper")
import time

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, DeleteView
from django.core.paginator import Paginator
from .models import Product
from .forms import ProductCreationForm
from scrapyd_api import ScrapydAPI
from scrapy.settings import Settings


# ScrapydAPI.schedule(project, spider, settings=None, **kwargs)

# project (string) The name of the project that owns the spider.
# spider (string) The name of the spider you wish to run.
# settings (dict) A dictionary of Scrapy settings keys you wish to override for this run.
# kwargs Any extra parameters you would like to pass to the spiders constructor/init method.

def scrapyd_run(request, product):
    """scrapyd_run 
    A function that takes a request and a product object and spawns
    a scrapyd process which runs a crawl on the specified URL passed from the Product object.

    Args:
        request ([object]): Request object passed from a Django view.
        product ([object]): Product model object returned from a form's form.save(commit=False)
    """
    project = "remind_me_scraper"

    scrapyd = ScrapydAPI('http://localhost:8080')
    # returns job id
    job_id = scrapyd.schedule(
        project, 
        spider="listings_spider",  
        # user_instance must be a tuple or we get an "object not iterable" error when passing it to our spider.
        user_instance=(request.user,),
        optional_product_name=product.name,
        URL=product.url)

    return job_id, scrapyd, project



def wait_till_finished(job_id, scrapyd, project):
    """Blocks until scrapyd.job_status returns 'finished'. 
    Once 'finished' is received, the function stops blocking.

    Args:
        job_id ([type]): [description]
        scrapyd ([type]): [description]
        project ([type]): [description]
    """
    while True:
        job_status = scrapyd.job_status(project, job_id)

        if job_status != "finished":
            print(f"Job status: {job_status}")
            while True:
                if job_status != scrapyd.job_status(project, job_id):
                    break
        else:
            print(f"--Job status: {job_status}!--")
            break


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
            # returns an instance of Product
            product_instance = product_form.save(commit=False)
            """ SpiderRunner(spider=ListingsSpider).scrape(user_instance=request.user, optional_product_name=product.name, URL=product.url) """

            # Runs the code that spawns a scrapyd process.
            job_id, scrapyd, project = scrapyd_run(request, product_instance)
            wait_till_finished(job_id, scrapyd, project)
            print(Product.objects.filter(author=user))
            
            newest_listing = Product.objects.filter(author=user).latest('date_added')
            print(newest_listing.name)
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
    template_name="listings/listing_home.html" # Default path: <app>/<model>_<viewtype>.html

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
        # Check if user who sent request is the user of that object
        if self.request.user == product.author:
            return True
        # Return False if not
        return False

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "listings/product_detail.html"
    context_object_name = "product"

    