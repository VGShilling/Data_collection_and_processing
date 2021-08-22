# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst, Join


def get_price(value):
    try:
        return float(value)
    except:
        return value


def get_specs(spec):
    result = spec.\
        replace('\n                ', '').\
        replace('\n                \n            ', '').\
        replace('\n            ', '')
    try:
        return float(result)
    except:
        return result


class LeroyparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field(output_processor=TakeFirst())
    photos = scrapy.Field()
    description = scrapy.Field(output_processor=Join())
    price = scrapy.Field(input_processor=MapCompose(get_price), output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    specs = scrapy.Field(output_processor=MapCompose(get_specs))
