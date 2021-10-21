# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import redis

r = redis.Redis(
    host='redis://:p8a075d8687be0f769ac6f3386fd4f7a8dd1003904bfce59edc77ed47a8b709a7@ec2-54-156-199-127.compute-1.amazonaws.com:23790',
    port=23790,
    password='p8a075d8687be0f769ac6f3386fd4f7a8dd1003904bfce59edc77ed47a8b709a7'
    )

class RemindMeScraperPipeline:
    def open_spider(self, spider):
        print("Spider Opened")

    def process_item(self, item, spider):

        print(item)
        return item
