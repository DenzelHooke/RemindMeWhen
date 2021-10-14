import time

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, DeleteView
from .models import Product
from .forms import ProductCreationForm
from remind_me_django.task_funcs import ScraperUtils

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
                time.sleep(1)
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
            product_instance = product_form.save(commit=False)

            # Runs the code that spawns a scrapyd process.
            job_id, scrapyd, project = ScraperUtils().scrapyd_first_run(request, product_instance)
            wait_till_finished(job_id, scrapyd, project)
            
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

    