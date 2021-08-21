import sys
sys.path.append("C:\\Users\\Denze\\Projects\\remindMe\\remind_me_django\\remind_me_scraper\\remind_me_scraper")
sys.path.append("C:\\Users\\Denze\\Projects\\remindMe\\remind_me_django")

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'remind_me_django.settings'

import django
django.setup()
from account.models import CustomUser

import scrapy
from remind_me_scraper.items import ProductItem
from ..item_loaders import ProductLoader

# url https://www.amazon.ca/WOODIES-Walnut-Sunglasses-Bamboo-Packaging/dp/B07VSV3T3X/ref=sr_1_38?dchild=1&keywords=sunglasses&qid=1629158228&sr=8-38&th=1
class ListingsSpider(scrapy.Spider):
    name = "listings_spider"
    user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
    

    def start_requests(self):
        yield scrapy.Request("https://www.amazon.ca/Seagate-Portable-External-Drive-STGX2000400/dp/B07CRG94G3?ref_=Oct_d_otopr_d_667823011&pd_rd_w=DOgyY&pf_rd_p=10a99ee7-57a7-4490-8aad-693d88d20b22&pf_rd_r=ZATFB95M0BSDR55FYC5C&pd_rd_r=fca75c53-f69d-4e5a-92f6-be142d2bbda8&pd_rd_wg=Ji5dl&pd_rd_i=B07CRG94G3", callback=self.parse)
    
    def parse(self, response):
        page = response.css("div.a-container")
        loader = ProductLoader(item = ProductItem(), selector=page)

        loader.add_value("url", response.url)
        loader.add_css("name", "span#productTitle")
        loader.add_css("price", "span#priceblock_ourprice")
        if page.css("div #availability span.a-size-medium a-color-success"):
            loader.add_value("stock", True)
        else:
            loader.add_value("stock", False)
        
        loader.add_value("author", CustomUser.objects.filter(email="denzelhooke@hotmail.com").first())

        yield loader.load_item()
        



        





