# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
import scrapy
from pymongo import MongoClient


class LeroyparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.scrapy_leroy

    def process_item(self, item, spider):
        if item['specs']:
            item['specs'] = self.process_to_dict(item['specs'])

        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

    def process_to_dict(self, specs):
        specs_dict = {specs[i]: specs[i + 1] for i in range(0, (len(specs) - 1), 2)}
        return specs_dict


class LeroyPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photos'] = [itm[1] for itm in results if itm[0]]
        return item



