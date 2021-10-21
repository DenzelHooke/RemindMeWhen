import time
import uuid

from listings.models import Product
from scrapyd_api import ScrapydAPI



#  ScrapydAPI.schedule(project, spider, settings=None, **kwargs)

# project (string) The name of the project that owns the spider.
# spider (string) The name of the spider you wish to run.
# settings (dict) A dictionary of Scrapy settings keys you wish to override for this run.
# kwargs Any extra parameters you would like to pass to the spiders constructor/init method.

class ScraperUtilz:
    def __init__(self, scrapyd_api):
        self._scrapyd_api = ScrapydAPI(scrapyd_api)
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

        Returns Job_id, project name, and scrapyd_api url.
        Args:
            user [object]: Product author object.
            product [object]: Product model object.
        """
        self._project_name = "remind_me_scraper"

        # returns job id
        self.__job_id = self._scrapyd_api.schedule(
            self._project_name, 
            spider="listings_spider",  
            # user_email must be a tuple or we get an "object not iterable" error when passing it to our spider.
            user_email=(user.email,),
            optional_product_name=product.name,
            URL=product.url)

        return self.__job_id, self._scrapyd_api, self._project_name

    def scrapyd_first_run(self, request, product):
        """
        scrapyd_run 
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

        return self.__job_id, self._scrapyd_api, self._project_name

    def wait_till_finished(self, time_to_poll):
        """
        Blocks until scrapyd.job_status returns "finished". 
        Once "finished" is received, the function stops blocking.

        Args:

            job_id (str): Job ID returned by scrapyd.schedule.
            scrapyd (Object): Scrapyd api object so we can poll the current job status.
            project (str): String of scrapyd project name deployed as egg to scrapyd.
            time_to_poll (int/float): Value used to determine how long it should take in between each poll (1 second recommended) .
        """
        while True:
            job_status = self._scrapyd_api.job_status(self._project_name, self.__job_id)

            if job_status != "finished":
                print(f"Job status: {job_status}")
                while True:
                    time.sleep(time_to_poll)
                    if job_status != self._scrapyd_api.job_status(self._project_name, self.__job_id):
                        break
            else:
                print(f"--Job status: {job_status}!--")
                break