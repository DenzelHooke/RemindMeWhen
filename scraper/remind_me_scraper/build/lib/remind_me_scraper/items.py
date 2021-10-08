# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class ProductItem(Item):
    # define the fields for your item here like:
    user_email = Field()
    name = Field()
    price = Field()
    stock = Field()
    url = Field()
    quantity = Field()

