import time
from uuid import uuid4

from scrapyd_api import ScrapydAPI



#  ScrapydAPI.schedule(project, spider, settings=None, **kwargs)

# project (string) The name of the project that owns the spider.
# spider (string) The name of the spider you wish to run.
# settings (dict) A dictionary of Scrapy settings keys you wish to override for this run.
# kwargs Any extra parameters you would like to pass to the spiders constructor/init method.

class ScraperUtilz:
    """Contains useful methods for running scrapyd processes with Django compatability.
    """
    scrapyd_api_url = 'http://scrapy:8080'                  


    def __init__(self):
        self._scrapyd_api = ScrapydAPI(ScraperUtilz.scrapyd_api_url)
        self._project_name:str = "remind_me_scraper"
        self.__job_id:str = None
        self.spider_name = "listings_spider"
        self.__uuid = uuid4()
          
    @property
    def job_id(self):
        return self.__job_id

    @property
    def uuid(self):
        return str(self.__uuid)


    def scrapyd_update_run(self, user, product):
        """
        A function that takes a user email and a product object and spawns
        a scrapyd process which runs a crawl on the specified URL passed from the Product object.

        Arguments:
            user {object} -- A django user object\n
            product {object} -- A django product lisiting object

        Returns:
            self.__job_id {str} -- Job ID of the scrapyd process\n
            self._scrapyd_api {object} -- Scrapyd api object\n
            self._project_name {str} -- scrapyd project name\n
        """

        # returns job id
        self.__job_id = self._scrapyd_api.schedule(
            self._project_name, 
            spider=self.spider_name,  
            # user_email must be a tuple or we get an "object not iterable" error when passing it to our spider.
            user_email=(user.email,),
            optional_product_name=product.name,
            URL=product.url,
            uuid=self.__uuid
            )

        return self.__job_id, self._scrapyd_api, self._project_name

    def scrapyd_first_run(self, request, product):
        """
        A function that takes a Django request object and a Django model product object and spawns
        a scrapyd process which runs a crawl on the specified URL passed from the Product object.

        Arguments:
            product {object} -- Product model object returned from a form's form.save(commit=False)\n
            request {object} -- Request object passed from a Django view.

        Returns:
            self.__job_id {str} -- Job ID of the scrapyd process\n
            self._scrapyd_api {object} -- Scrapyd api object\n
            self._project_name {str} -- scrapyd project name\n
        """

        # returns job id
        self.__job_id = self._scrapyd_api.schedule(
            self._project_name, 
            spider=self.spider_name,  
            # user_instance must be a tuple or we get an "object not iterable" error when passing it to our spider.
            user_email=(request.user,),
            optional_product_name=product.name,
            URL=product.url,
            uuid=self.__uuid
            )

        return self.__job_id, self._scrapyd_api, self._project_name

    def get_job_status(self):
        """Simply returns the job status of the most recently ran job on this object

        Returns:
            job_status: scrapyd str of the most recently ran job on this object.
        """
        job_status = self._scrapyd_api.job_status(self._project_name, self.__job_id)
        return job_status

    def wait_till_finished(self, time_to_poll):
        """
        Blocks until scrapyd.job_status returns "finished". 
        Once "finished" is received, the function stops blocking.

        Arguments:

            job_id {str} -- Job ID returned by scrapyd.schedule.\n
            scrapyd {Object} -- Scrapyd api object so we can poll the current job status.\n
            project {str} -- String of scrapyd project name deployed as egg to scrapyd.\n
            time_to_poll {int/float} -- Value used to determine how long it should take in between each poll (1 second recommended) .
        """


        while True:
            job_status = self._scrapyd_api.job_status(self._project_name, self.__job_id)
            print(job_status)
            if job_status != "finished":
                print(f"Job status: {job_status}")
                while True:
                    time.sleep(time_to_poll)
                    if job_status != self._scrapyd_api.job_status(self._project_name, self.__job_id):
                        break
            else:
                print(f"--Job status: {job_status}!--")
                break

