import sys
sys.path.append("C:\\Users\\Denze\\Projects\\remindMe\\remind_me_django")
sys.path.append("C:\\Users\\Denze\\Projects\\remindMe\\remind_me_scraper/remind_me_scraper")
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'remind_me_django.settings'

import django
django.setup()

import scrapy
from items import ProductItem
from item_loaders import ProductLoader
from account.models import CustomUser

# url https://www.amazon.ca/WOODIES-Walnut-Sunglasses-Bamboo-Packaging/dp/B07VSV3T3X/ref=sr_1_38?dchild=1&keywords=sunglasses&qid=1629158228&sr=8-38&th=1

# To allow spider to work with scrapyd, spider init must allow for unspecifed number of args and kwargs (*args, **kwargs)
#  


class ListingsSpider(scrapy.Spider):

    def __init__(self, user_instance, URL, optional_product_name=None, *args, **kwargs):
        self.user_instance = CustomUser.objects.filter(email=user_instance).first()
        print(f"DEBUG: {self.user_instance}")

        # User input
        self.optional_product_name = optional_product_name
        self.URL = URL

    name = "listings_spider"
    user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
    

    def start_requests(self):
        yield scrapy.Request(self.URL, callback=self.parse)
    
    def parse(self, response):
        page = response.css("div.a-container")
        loader = ProductLoader(item = ProductItem(), selector=page)

        if self.optional_product_name:
            loader.add_value("name", self.optional_product_name)
        else:
            loader.add_css("name", "span#productTitle")
            
        loader.add_value("url", self.URL)
        
        price = page.css("div #priceInsideBuyBox_feature_div div span:nth-child(1)").get()
        loader.add_value("price", price)

        if page.css("div #availability span.a-size-medium a-color-success"):
            loader.add_value("stock", True)
        else:
            loader.add_value("stock", False)
        
        loader.add_value("author", self.user_instance)

        yield loader.load_item()
        



        





