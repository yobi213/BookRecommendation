# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from __future__ import unicode_literals
from scrapy.exporters import JsonItemExporter,CsvItemExporter
from scrapy.conf import settings
from scrapy.exceptions import DropItem
from scrapy import log

import pymongo

class MongoDBPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0|!".format(data))

        if valid:
            self.collection.insert(dict(item))
            log.msg("Reviews added to MongoDB database!",
                    level = log.DEBUG, spider=spider)
        return item


class CsvPipeline(object):
    def __init__(self):
        self.file = open("page_list.csv",'wb')
        self.exporter = CsvItemExporter(self.file,encoding='utf-8')
        self.exporter.start_exporting()

    def close_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class JsonPipeline(object):
    def __init__(self):
        self.file = open("naverBook.json",'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
