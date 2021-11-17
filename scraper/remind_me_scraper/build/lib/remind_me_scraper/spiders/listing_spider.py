import re
import sys
sys.path.append("remindme_scraper/remind_me_scraper")
# find a better way for production ^^

import scrapy
from ..items import ProductItem
from ..item_loaders import ProductLoader

# url https://www.amazon.ca/WOODIES-Walnut-Sunglasses-Bamboo-Packaging/dp/B07VSV3T3X/ref=sr_1_38?dchild=1&keywords=sunglasses&qid=1629158228&sr=8-38&th=1

# To allow spider to work with scrapyd, spider init must allow for unspecifed number of args and kwargs (*args, **kwargs)

# Don't forget to redeploy your project to scrapyd after each change you make within the scraper directory or else the changes won't take effect on the container.

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
        page = response.css("div.a-container")
        loader = ProductLoader(item=ProductItem(), selector=page)

        if self.optional_product_name:
            loader.add_value("name", self.optional_product_name)
        else:
            loader.add_css("name", "span#productTitle")
            
        loader.add_value("url", self.URL)
        
        # stock_list = [
        #     self.get_out_of_stock("span .a-color-price a-text-bold div span:nth-child(1)", page, 'Currently unavailable.'),
        # ]
        # out_of_stock = self.check_value(stock_list)

        out_of_stock = False

        price_list = [
            page.xpath("//span[@id='price_inside_buybox']/text()").extract(),
        ]

        test_price = '<span>10</span>' 
        price = self.check_value(price_list)
        
        # if out_of_stock:
        #     loader.add_value("stock", 0)
        #     loader.add_value("price", '0')
        # else:
        loader.add_value("stock", 1)
        loader.add_value("price", page.xpath("//div[@id='corePrice_feature_div']//span[@class='a-offscreen']/text()").extract())
        
        loader.add_value("user_email", self.user_email)
        loader.add_value("uuid", self.uuid)
        
        yield loader.load_item()
    

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
    
    def get_out_of_stock(self, selector, page, expected_text):

        if page.css(selector).get() == expected_text:
            return True
        else:
            return False
        








