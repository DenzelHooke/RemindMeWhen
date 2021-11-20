import re
from datetime import datetime as dt, timedelta
from random import randrange
import sys
sys.path.append("remindme_scraper/remind_me_scraper")
# find a better way for production ^^

import scrapy
from ..items import ProductItem
from ..item_loaders import ProductLoader
import pytz
import redis


# url https://www.amazon.ca/WOODIES-Walnut-Sunglasses-Bamboo-Packaging/dp/B07VSV3T3X/ref=sr_1_38?dchild=1&keywords=sunglasses&qid=1629158228&sr=8-38&th=1

# To allow spider to work with scrapyd, spider init must allow for unspecifed number of args and kwargs (*args, **kwargs)

# Don't forget to redeploy your project to scrapyd after each change you make within the scraper directory or else the changes won't take effect on the container.



r = redis.Redis(host='redis', port=6379, db=0)


class ListingsSpider(scrapy.Spider):

    
    def __init__(self, user_email, URL, optional_product_name=None, uuid=None, *args, **kwargs):
        self.user_email = user_email
        print(f"DEBUG: {self.user_email}")

        # User input
        self.optional_product_name = optional_product_name
        self.URL = URL
        self.uuid = uuid

    name = "listings_spider"
    user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
    

    def start_requests(self):
        yield scrapy.Request(self.URL, callback=self.parse)
    
    def parse(self, response):
        
        page = response.css("div#ppd")
        loader = ProductLoader(item=ProductItem(), selector=page)

        if page:
            print("page found!")
            if self.optional_product_name:
                loader.add_value("name", self.optional_product_name)
            else:
                loader.add_css("name", "span#productTitle")
            
            # loader.add_xpath("name", "//span[@id='productTitle']/text()")
            loader.add_value("url", self.URL)
            
            stock_list = [
                self.out_of_stock(
                    "//div[@id='availability']//span[@class='a-size-medium a-color-state']/text()", 
                    page, 
                    'Currently unavailable.'
                ),
                self.in_stock(
                    "//div[@id='availability']//span[@class='a-size-medium a-color-success']/text()", 
                    page, 
                    'In Stock.'
                ),
            ]
            # out_of_stock = self.check_value(stock_list)

            out_of_stock = False
            test_price = '<span>10</span>' 



            price_list = [
                page.xpath("//div[@id='corePrice_feature_div']//span[@class='a-offscreen']/text()").extract()
            ]

            # test_price = '<span>10</span>' 

            price = self.check_value(price_list)
            
            if not price:
                loader.add_value("stock", False)
                loader.add_value("price", '<span>0</span>')

            else:
                loader.add_value("stock", True)
                loader.add_value("price", price)
                
            
            loader.add_value("user_email", self.user_email)
            loader.add_value("uuid", self.uuid)
            
            yield loader.load_item()

        if r.get('slowdown'):
            # If this already exists, do nothing
            pass

        else:
            print("**page NOT found**")
            # Set a slowdown str within Redis
            utc_now = pytz.utc.localize(dt.utcnow())
            r.set("slowdown", str(utc_now))
            r.expire("slowdown", 80)
            print("---slowdown SET!---")

        

    def check_value(self, value_list):
        """
        Loops through each return value of a CSS selector and verifies that there is only one price value.
        This allows us to have multiple css selectors but only use the return value that's True

        Args:
            page (object): parse method page response object.
            loader (object): item loader object also from the parse method.

        Returns:
            p
        """
        value_verify = []

        for value in value_list:
            if value:
                value_verify.append(value)
        
        if len(value_verify) == 1:
            return value_verify[0]
        return None
    
    def out_of_stock(self, selector, page, expected_text=None):
        text = page.xpath(selector).extract()

        if text == expected_text:
            return 'out of stock'

        elif 'In stock on' in text:
            return 'out of stock'
            
        else:
            return None
        
    def in_stock(self, selector, page, expected_text):
        if page.xpath(selector).extract() == expected_text:
            return 'in stock'
        else:
            return None
    











