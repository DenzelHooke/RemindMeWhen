# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from twisted.internet.error import TCPTimedOutError, TimeoutError
from scrapy.core.downloader.handlers.http11 import TunnelError

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
import base64
import redis
import random
import logging



r = redis.Redis(host='redis', port=6379, db=0)

class RemindMeScraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RemindMeScraperDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ProxyMiddleware:
    def process_request(self, request, spider):
        fresh_proxies = r.lrange('https_proxies', 0, -1)
        bad_proxies = r.lrange('bad_proxies', 0, -1)
        # good proxy 'https://185.20.198.213:22800' 
        # Bad proxy https://181.230.171.176:8080
        if fresh_proxies:
            choice = random.choice(fresh_proxies)
             
            if choice not in bad_proxies:
                request.meta['proxy'] = 'https://181.230.171.176:8080' 
                r.set('proxy_last_used', request.meta['proxy'])
                return request
        else:
            pass

# https://stackoverflow.com/questions/44698626/how-to-handle-timeout-using-scrapy
class RetrySpiderMiddleware(RetryMiddleware):

    def process_exception(self, request, exception, spider):
        # Retry scrape if any of these exceptions are met.
        if isinstance(exception, TimeoutError) or isinstance(exception, TCPTimedOutError) or isinstance(exception, TypeError) or isinstance(exception, TunnelError):
            # Store proxy within ban list
            bad_proxy = request.meta['proxy']
            r.lpush('bad_proxies', bad_proxy)
            print(f'Bad proxy detected: {bad_proxy}')
            
            return None
            # return self._retry(request, exception,  spider)



class TestProxyRejectMiddleware(RetryMiddleware):

    def process_exception(self, request, exception, spider):
        # Retry scrape if any of these exceptions are met.
        if isinstance(exception, TimeoutError) or isinstance(exception, TCPTimedOutError) or isinstance(exception, TypeError) or isinstance(exception, TunnelError):
            # Store proxy within ban list
            bad_proxy = request.meta['proxy']
            r.lpush('bad_proxies', bad_proxy)
            print(f'Bad proxy detected: {bad_proxy}')
        
            return exception