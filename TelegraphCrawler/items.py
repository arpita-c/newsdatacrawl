# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item, Field

#class WebcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
 #   pass


class ScrapyItem(scrapy.Item):
    link = Field()
    childlink=Field()
    childlinkcontent=Field()
    pass
    #title = Field() 
    #content = Field()

class ScrapyItemDetails(scrapy.Item):
    headline = Field()
    datetime=Field()
    content=Field()
    url=Field()

    pass
    #title = Field() 
    #content = Field()



