# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    user_id = scrapy.Field()
    username = scrapy.Field()
    picture = scrapy.Field()
    the_way = scrapy.Field()
    parsed_user_id = scrapy.Field()
    parsed_username = scrapy.Field()

