import os
import re
from datetime import datetime as dt, timedelta
import random 
import sys
# sys.path.append("remindme_scraper/remind_me_scraper")
# find a better way for production ^^

import scrapy
from ..items import ProductItem
from .. item_loaders import ProductLoader
import pytz
import redis


# url https://www.amazon.ca/WOODIES-Walnut-Sunglasses-Bamboo-Packaging/dp/B07VSV3T3X/ref=sr_1_38?dchild=1&keywords=sunglasses&qid=1629158228&sr=8-38&th=1

# To allow spider to work with scrapyd, spider init must allow for unspecifed number of args and kwargs (*args, **kwargs)

# Don't forget to redeploy your project to scrapyd after each change you make within the scraper directory or else the changes won't take effect on the container.

# Unavailable product pages

# https://www.amazon.ca/Water-Positive-Pregnancy-Domestic-Priority/dp/B07D35C7VK/ref=sr_1_8?keywords=test&qid=1637548524&refinements=p_n_availability%3A12035748011&rnid=12035746011&sr=8-8

# out of stock messages

# Temporarily out of stock.
# Currently unavailable.
# In stock on

# job = project.jobs.run(
#     'listings_spider',
#     job_args={
#     'uuid':uuid,
#     'user_email':email,
#     'URL':url}
#     )
class ListingsSpider(scrapy.Spider):
    def __init__(self, user_email, URL, uuid, optional_product_name=None):
        self.user_email = user_email
        # print(f"DEBUG: {self.user_email}")

        # User input
        self.optional_product_name = optional_product_name
        self.URL = URL
        self.uuid = uuid

    name = "listings_spider"
    # user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0'
    # user_agent = None
    

    def start_requests(self):
        yield scrapy.Request(
            self.URL, 
            callback=self.parse)
    
    def parse(self, response):
        # div#dp-container
        # page = response.css("div#ppd")
        page = response.css("div#dp-container")
        loader = ProductLoader(item=ProductItem(), selector=page)

        print(page)
        if page:
            print("page found!")
            if self.optional_product_name:
                loader.add_value("name", self.optional_product_name)
            else:
                loader.add_css("name", "span#productTitle")

            loader.add_value("url", self.URL)
            
            stock_list = [
                page.xpath("//div[@id='availability']//span[@class='a-size-medium a-color-success']/text()").extract(),
            ]

            price_list = [
                page.xpath("//div[@id='corePrice_feature_div']//span[@class='a-offscreen']/text()").extract()
            ]

            # Had to change this code to pythons.7 compatiable due ot scraping hub being 2.7
            print(f"STOCK_LIST: {stock_list}")
            print(f"PRICE_LIST: {price_list}")

            # test_price = '<span>10</span>' 
            price = self.check_value(price_list)

            if not stock_list[0]:
                print("--Stock element not found.--")
                stock = False
            else:
                print("--Stock element found.--")
                stock = stock_list[0][0].lower().replace('.', '').replace(',', '').strip()


            status_1 = "temporarily out of stock"
            status_2 = "currently unavailable"
            status_3 = "in stock on"
            status_4 = "in stock"
            status_5 = "only"

            
            if not price:
                loader.add_value("stock", False)
                loader.add_value("price", '<span>0</span>')

            else:
                if stock == False:
                    loader.add_value("stock", False)
                # If out of stock:
                elif stock == status_1:
                    loader.add_value("stock", False)
                # If in stock:
                elif stock == status_4:
                    loader.add_value("stock", True)
                elif stock == status_2:
                    loader.add_value("stock", False)
                elif status_3 in stock:
                    loader.add_value("stock", False)
                elif status_5 in stock:
                    loader.add_value("stock", True)
                
                loader.add_value("price", price)
                
            
            loader.add_value("user_email", self.user_email)
            loader.add_value("uuid", self.uuid)
            
            yield loader.load_item()

        else:
            print("**page NOT found**")
            # r.get("celery-slowdown")
            # #  add 
            # # Set a slowdown str within Redis
            # utc_now = pytz.utc.localize(dt.utcnow())
            # r.set("slowdown", str(utc_now))
            # r.expire("slowdown", 10)
            # print("---slowdown SET!---")
            # if r.get(f"MANUAL_SCRAPE-{str(self.uuid)}"):




        
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
    











