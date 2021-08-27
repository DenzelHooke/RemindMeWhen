import sys
sys.path.append("C:\\Users\\Denze\\Projects\\remindMe\\remind_me_scraper\\remind_me_scraper")

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from .models import Product
from .forms import ProductCreationForm

from scrapyd_api import ScrapydAPI

from scrapy.settings import Settings
from spiders.listing_spider import ListingsSpider
from scraper_code import SpiderRunner


# ScrapydAPI.schedule(project, spider, settings=None, **kwargs)

# project (string) The name of the project that owns the spider.
# spider (string) The name of the spider you wish to run.
# settings (dict) A dictionary of Scrapy settings keys you wish to override for this run.
# kwargs Any extra parameters you would like to pass to the spiders constructor/init method.


def scrapyd_run(request, product, *args, **kwargs):
    scrapyd = ScrapydAPI('http://localhost:8080')
    scrapyd.schedule(
        project="remind_me_scraper", 
        spider="listings_spider",  
        user_instance=(request.user,),
        optional_product_name=product.name, 
        URL=product.url)

# Problem may be something with user_instance returning a string? or request.user returning string?
# Problem may be something with user_instance returning a string? or request.user returning string?
@login_required
def listing_add(request):
    context = {}
    if request.method == "POST":
        product_form = ProductCreationForm(request.POST)
        if product_form.is_valid():
            print(f"-------------{request.user}-------------")
            # returns an instance of Product
            product = product_form.save(commit=False)   
            """ SpiderRunner(spider=ListingsSpider).scrape(user_instance=request.user, optional_product_name=product.name, URL=product.url) """
            scrapyd_run(request, product)

    else:
        product_form = ProductCreationForm()
        
    context['form'] = product_form
    return render(request, "listings/listing_landing.html", context)


class ProductListView(ListView):
    model = Product
    template_name="listings/listing_home.html"
    context_object_name = "products"