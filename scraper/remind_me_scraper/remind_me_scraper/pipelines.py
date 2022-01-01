import json
import os
import redis
from decouple import config
from .settings import REDIS_HOST, REDIS_PASS, REDIS_PORT
# from django.forms.widgets import URLInput
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# If you ever get this error: 
#   File "/app/python/lib/python3.8/site-packages/redis/connection.py", line 1304, in get_connection
#     connection = self._available_connections.pop()
# IndexError: pop from empty list
# It's most likely because one of your redis env vars aren't correct. 
REDIS_PASS = 'WpuQ60Fb6hE9OcBSZiSIOa32474294d'
REDIS_HOST = 'redis-16583.c84.us-east-1-2.ec2.cloud.redislabs.com'
REDIS_PORT = 16583
pool = redis.ConnectionPool(
    host=REDIS_HOST, 
    password=REDIS_PASS, 
    port=REDIS_PORT , 
    db=0
    )
r = redis.Redis(connection_pool=pool)


class RemindMeScraperPipeline:
    # Had a problem where I added item as a param and that caused the spider to fail
    def open_spider(self, spider):
        r.set('open_spider', 1)
        print("Spider Opened")

    def process_item(self, item, spider):
        print("processing_item")
        item = dict(item)
        uuid = item['uuid']
        json_response = json.dumps(item)
        r.set(uuid, json_response)
        r.expire(uuid, 30)
        return item


# Don't forget to redeploy your project to scrapyd after each change you make within the scraper directory or else the changes won't take effect on the container.