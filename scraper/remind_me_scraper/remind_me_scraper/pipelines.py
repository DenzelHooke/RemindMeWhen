# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class RemindMeScraperPipeline:
    def open_spider(self, spider):
        print("Spider Opened")

    def process_item(self, item, spider):
        # Item = model instance
        # Connect to DB and save object in DB.
        item.save()
        return item
