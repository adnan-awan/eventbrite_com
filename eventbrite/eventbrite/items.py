# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst, Join, MapCompose


class EventbriteItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    description = scrapy.Field()
    url = scrapy.Field()
    cost = scrapy.Field()
    location = scrapy.Field()
    id = scrapy.Field()
    parent_id = scrapy.Field()
    status = scrapy.Field()
    start_datetime = scrapy.Field()
    end_datetime = scrapy.Field()
    start_timezone = scrapy.Field()
    end_timezone = scrapy.Field()
    locale = scrapy.Field()
    image_url = scrapy.Field()
    summary = scrapy.Field()
    meta_description = scrapy.Field()
    canonical_url = scrapy.Field()


class EventbriteItemLoader(ItemLoader):
    default_input_processor = MapCompose(str.strip)
    default_output_processor = TakeFirst()
    description_out = Join()
    location_out = Join()
