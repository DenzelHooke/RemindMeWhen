from listings.models import Product
from scrapyd_api import ScrapydAPI



#  ScrapydAPI.schedule(project, spider, settings=None, **kwargs)

# project (string) The name of the project that owns the spider.
# spider (string) The name of the spider you wish to run.
# settings (dict) A dictionary of Scrapy settings keys you wish to override for this run.
# kwargs Any extra parameters you would like to pass to the spiders constructor/init method.

class ScraperUtils:
    def __init__(self):
        self._scrapyd_api = ScrapydAPI('http://scrapy.com')
        self._project_name = None
        self.__job_id = None
          
    @property
    def job_id(self):
        return self.__job_id

    def scrapyd_update_run(self, user, product):
        """
        scrapyd_update_run 
        A function that takes a user email and a product object and spawns
        a scrapyd process which runs a crawl on the specified URL passed from the Product object.

        Args:
            user [object]: Product author object.
            product [object]: Product model object.
        """
        self._project_name = "remind_me_scraper"

        # returns job id
        self.__job_id = self._scrapyd_api.schedule(
            self._project, 
            spider="listings_spider",  
            # user_email must be a tuple or we get an "object not iterable" error when passing it to our spider.
            user_email=(user.email,),
            optional_product_name=product.name,
            URL=product.url)

        return self.__job_id, self._scrapyd_api, self._project

    def scrapyd_first_run(self, request, product):
        """scrapyd_run 
        A function that takes a request and a product object and spawns
        a scrapyd process which runs a crawl on the specified URL passed from the Product object.

        Args:
            request ([object]): Request object passed from a Django view.
            product ([object]): Product model object returned from a form's form.save(commit=False)
        """
        self._project_name = "remind_me_scraper"

        # returns job id
        self.__job_id = self._scrapyd_api.schedule(
            self._project_name, 
            spider="listings_spider",  
            # user_instance must be a tuple or we get an "object not iterable" error when passing it to our spider.
            user_email=(request.user,),
            optional_product_name=product.name,
            URL=product.url)

        return self.__job_id, self._scrapyd_api, self._project