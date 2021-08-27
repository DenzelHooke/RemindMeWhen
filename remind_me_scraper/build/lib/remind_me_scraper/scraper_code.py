from scrapy.crawler import CrawlerRunner
from twisted.internet import reactor
from multiprocessing import Process, Queue
from scrapyd_api import ScrapydAPI


# def run_spider(spider, user_instance, optional_product_name, URL):
#     def f(q):
#         try:
#             runner = CrawlerRunner()
#             deffered = runner.crawl(
#                 spider = spider,
#                 user_instance = user_instance, 
#                 optional_product_name = optional_product_name,
#                 URL = URL,  
#             )
#             deffered.addBoth(lambda _: reactor.stop())

#             print("----Scraping Started----")
#             reactor.run()
#             print("----Scraping Complete----")
#             q.put(None)

#         except Exception as e:
#             q.put(e)

#     q = Queue()
#     p = Process(target=f, args=(q,))
#     p.start()
#     p.join()

scrapyd = ScrapydAPI('http://localhost:8080')


class SpiderRunner():
    def __init__(self, spider):
        
        self.runner = CrawlerRunner()
        self.__spider = spider
    
    def scrape(self, user_instance, optional_product_name, URL):
        self.deffered = self.runner.crawl(
            self.__spider, 
            user_instance = user_instance, 
            optional_product_name = optional_product_name,
            URL = URL,
        )
        self.deffered.addBoth(lambda _: reactor.stop())

        print("----Scraping Started----")
        reactor.run()
        print("----Scraping Complete----")
