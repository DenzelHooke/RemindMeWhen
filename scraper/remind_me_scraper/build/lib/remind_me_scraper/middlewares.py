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
import time
from .settings import USER_AGENTS



r = redis.Redis(host='redis', port=6379, db=0)
class NoProxiesAvailable(Exception):
    def __init__(self, message='No proxies available!'):
        super().__init__(self, message)


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
        if isinstance(exception, TypeError):
            print('TYPE ERROR')
            # Store proxy within ban list
            bad_proxy = request.meta['proxy']
            r.lpush('bad_proxies', bad_proxy)
            print(f'Bad proxy detected: {bad_proxy}')

        return request
        
class RandomUserAgentMiddleware():
    def process_request(self, request, spider):
        request.dont_filter = True
        ua = random.choice(USER_AGENTS)
        request.headers.setdefault('User-Agent', ua)
        
        print(f'---Request Headers:{request.headers}---')

# 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36'
# 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36'
class ProxyMiddleware:
    error_limit = 2

    def process_request(self, request, spider):
        fresh_proxies = r.lrange('https_proxies', 0, -1)
        bad_proxies = r.lrange('bad_proxies', 0, -1)

        print(f'---ProxyMiddleware: {request.headers}---')
        if fresh_proxies:
            while True:
                choice = random.choice(fresh_proxies)
                if choice not in bad_proxies:
                    break
                else:
                    if len(bad_proxies) == len(fresh_proxies):
                        raise NoProxiesAvailable


            request.meta['proxy'] = choice
            # spider.log(f"proxy-used: {request.meta['proxy']}",level=log.DEBUG)
            print(f'---Request Proxy:{request.meta}---')
            r.set('proxy_last_used', request.meta['proxy'])
    
    def process_exception(self, request, exception, spider):
        # Retry scrape if any of these exceptions are met.
        print('--- EXCEPTION MIDDLEWARE HIT ---')
        if isinstance(exception, TypeError):
            print('TYPE ERROR')

            bad_proxy = request.meta['proxy']
            error_count = r.get(f'{bad_proxy}-fail-count')
            # Checks if there's been a previous error with this proxy
            if error_count:
                r.set(f'{bad_proxy}-fail-count', int(error_count)+1)

            else:
                r.set(f'{bad_proxy}-fail-count', 1)

            # Store proxy within ban list

            if int(r.get(f'{bad_proxy}-fail-count')) == ProxyMiddleware.error_limit:
                r.lpush('bad_proxies', bad_proxy)
                # r.set('bad_proxy_last_used', 'None')
                r.delete(f'{bad_proxy}-fail-count')
                 
            print(f'Bad proxy detected: {bad_proxy}')

            time.sleep(3)
            # return request

