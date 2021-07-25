from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.quotes_spider import QuoteSpider
from scrapy.settings import Settings



class SpiderScript():

    def __init__(self, spider_name): 
        # Starts twisted reactor 
        # https://docs.scrapy.org/en/latest/topics/practices.html

        # transfers over our current projects spiders and pipelines into a settings object
        self.settings = get_project_settings()
        self.process = CrawlerProcess(self.settings)
        self.spider_name = spider_name

    def run_spider(self):
        # Finds a spider with this name in a scrapy project using spider loader, then creates a Crawler instance for it
        self.spider = self.process.crawl(self.spider_name)
         # the script will block here until the crawling is finished
        self.process.start()



spider = SpiderScript(QuoteSpider).run_spider()

