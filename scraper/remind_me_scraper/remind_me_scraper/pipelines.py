import json
import redis
from django.forms.widgets import URLInput
from itemadapter import ItemAdapter

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface


class RemindMeScraperPipeline:
    def open_spider(self, spider):
        self.r = redis.Redis(host='redis', port=6379, db=0)
        self.r.set('open_spider', 1)
        print("Spider Opened")

    def process_item(self, item, spider):
        print("processing_item")
        item = dict(item)
        uuid = item['uuid']
        json_response = json.dumps(item)
        self.r.set(uuid, json_response)
        self.r.expire(uuid, 15)
        return item


# Don't forget to redeploy your project to scrapyd after each change you make within the scraper directory or else the changes won't take effect on the container.