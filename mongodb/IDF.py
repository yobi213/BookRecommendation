#-*- coding: utf-8 -*-
from pymongo import MongoClient
import math

class make_idf:

    def __init__(self):
        client = MongoClient("110.34.84.101", 3100)
        db = client.crawl_naver_cat5
        self.collection_tag = db.point_percent_economy
        self.collection_idf = db.point_idf_economy

    def make_words_list(self):
        set_tag = set()

        for col in self.collection_tag.find({}):
            s = set(col['tag_percent'].keys())
            set_tag = set_tag | s

        dict_idf = dict.fromkeys(set_tag, 0)

        return dict_idf


    def idf(self, keyword):
        find_tag = 'tag_percent.' + keyword  # mongodb 명령어 규칙을 따름
        self.collection_tag.count({find_tag: {'$exists': 'true'}})
        idf = math.log10(self.collection_tag.count({}) / self.collection_tag.count({find_tag: {'$exists': 'true'}}))

        return idf


    def make_dict(self):
        dict = self.make_words_list()
        key_list = dict.keys()

        for row in key_list:
            dict[row] = self.idf(row)
            print(dict[row])

        return dict


    def make_idf_DB (self):
        try:
            self.collection_idf.insert(self.make_dict())
        except TypeError:
            print("Error")

        print("save completely")


#Execution
tt = make_idf()
tt.make_words_list()
tt.make_idf_DB()



