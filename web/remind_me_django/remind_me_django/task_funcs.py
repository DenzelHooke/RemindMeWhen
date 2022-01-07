import time
import os
import requests
import logging
from bs4 import BeautifulSoup
from uuid import uuid4
from scrapyd_api import ScrapydAPI
from scrapinghub import ScrapinghubClient
from .settings import SCRAPING_HUB_API, SCRAPING_HUB_PROJECT
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'remind_me_django.settings'
django.setup()

#  ScrapydAPI.schedule(project, spider, settings=None, **kwargs)

# project (string) The name of the project that owns the spider.
# spider (string) The name of the spider you wish to run.
# settings (dict) A dictionary of Scrapy settings keys you wish to override for this run.
# kwargs Any extra parameters you would like to pass to the spiders constructor/init method.

class ScraperUtilz:
    """Contains useful methods for running scrapyd processes with Django compatability.
    """
    def __init__(self, state=None):
        if state == "dev":
            self.scrapyd_api_url = 'http://scrapy:8080'                  
            self._scrapyd_api = ScrapydAPI(ScraperUtilz.scrapyd_api_url)
        elif state == 'production':
            
            self.__client = ScrapinghubClient(SCRAPING_HUB_API)
            self.__project = self.__client.get_project(SCRAPING_HUB_PROJECT)

        self._project_name:str = "remind_me_scraper"
        self.__job_id:str = None
        self._spider_name = "listings_spider"
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
            spider=self._spider_name,  
            # user_email must be a tuple or we get an "object not iterable" error when passing it to our spider.
            user_email=(user.email,),
            optional_product_name=product.name,
            URL=product.url,
            uuid=self.__uuid
            )

        return self.__job_id, self._scrapyd_api, self._project_name

    def scrapinghub_update_run(self, user, product):
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
            spider=self._spider_name,  
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
            spider=self._spider_name,  
            # user_instance must be a tuple or we get an "object not iterable" error when passing it to our spider.
            user_email=(request.user,),
            optional_product_name=product.name,
            URL=product.url,
            uuid=self.__uuid
        )

        return self.__job_id, self._scrapyd_api, self._project_name

    def scrapyd_get_job_status(self):
        """Simply returns the job status of the most recently ran job on this object

        Returns:
            job_status: scrapyd str of the most recently ran job on this object.
        """
        job_status = self._scrapyd_api.job_status(self._project_name, self.__job_id)
        return job_status

    def wait_till_finished(self, time_to_poll=1, state='dev', limit=None):
        """
        Blocks until scrapyd.job_status returns "finished". 
        Once "finished" is received, the function stops blocking.

        Arguments:

            job_id {str} -- Job ID returned by scrapyd.schedule.\n
            scrapyd {Object} -- Scrapyd api object so we can poll the current job status.\n
            project {str} -- String of scrapyd project name deployed as egg to scrapyd.\n
            time_to_poll {int/float} -- Value used to determine how long it should take in between each poll (1 second recommended) .
        """
        flag = False
        count = 0
        if limit:
            time_limit = limit
        else:
            time_limit = 120

        while not flag:
            if state == 'dev':
                job_status = self._scrapyd_api.job_status(self._project_name, self.__job_id)
            elif state == 'production':
                job_status = self.scrapinghub_get_job_status()
            if job_status != "finished":
                print(f"Job status: {job_status}")
                while True:
                    time.sleep(time_to_poll)
                    count +=1
                    
                    if count >= time_limit:
                        flag = True
                        logging.debug('wait_till_finished func: LIMIT HIT. BREAKING LOOP')
                        break
                    if state == 'dev':
                        if job_status != self._scrapyd_api.job_status(self._project_name, self.__job_id):
                            break
                    elif state == 'prod':
                        if job_status != self.scrapinghub_get_job_status():
                            break
                        

            else:
                print(f"--Job status: {job_status}!--")
                break
    
    def scrapinghub_first_run(self, user, product_form, product_name=None):
        
        job = self.__project.jobs.run(
            self._spider_name,  
            job_args={
                'user_email':(user,),
                'optional_product_name':product_form['name'],
                'URL':product_form['url'],
                'uuid':self.__uuid
            }
        )
        self.__job_id = job.key
    
    def scrapinghub_get_job_status(self):
        return self.__project.jobs.get(self.__job_id).metadata.get('state')

def update_prod_last_updated(product, current_time):
    product.last_updated = current_time
    product.save()

def scrape_https_proxies(proxy_list):
    """
    Scrape proxies and return an iterable with acceptable proxies.

    Args:
        proxy_list (list): List of free proxy website url strings.
    """

    parser = 'lxml'
    good_proxies = []

    for url in proxy_list:
        soup = BeautifulSoup(requests.get(url).text, parser)
        # free-proxy-list.net
        if url == 'https://free-proxy-list.net/':
            # Get Table of data
            tbody = soup.find('tbody')

            # loop thru each table row
            for tr in tbody.find_all('tr'):
                # Create a list of all td within this table row
                td_list = [td.text for td in tr.find_all('td')]
                # Filter out bad proxies if they're elite proxy and https
                if td_list[4] == 'elite proxy' and td_list[6] == 'yes':
                    proxy = f'https://{td_list[0]}:{td_list[1]}'
                    # Append string 
                    good_proxies.append(proxy)
    logging.debug(good_proxies)
    return good_proxies



