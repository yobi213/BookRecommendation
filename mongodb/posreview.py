# -*- coding: utf-8 -*-
from pymongo import MongoClient
from konlpy.tag import Mecab
from konlpy.utils import pprint


class Tagging_DB:
    def __init__(self):
        client = MongoClient("110.34.84.101", 3100)
        db_review = client.crawl_naver_cat5
        #불러오는 raw_collection
        self.collection_review = db_review.raw_reviews_economy
        #저장하는 pos collection
        db_pos = client.books_pos
        self.collection_pos = db_pos.pos_reviews_economy

    def pos_by_ISBN(self, contents):
        mecab = Mecab()
        pos_list = []

        for col in self.collection_review.find({"ISBN" : contents},{"_id" : 0, "review_text" : 1}):
            pos = mecab.pos(col['review_text'])
            pos_list.append(pos)

        return pos_list


    def make_pos_DB (self, contents):
        bookinfo = self.collection_review.find_one({"ISBN" : contents}, {"_id" : 0, "review_text" : 0})
        self.collection_pos.insert(bookinfo)
        pos_list = self.pos_by_ISBN(contents)
        self.collection_pos.update({"ISBN": contents}, {"$set" : {"reviews_pos" : pos_list}})
        # self.collection_pos.update({"title": contents}, {"$set" : {"reviews_pos" : self.pos_by_ISBN(contents)}}, upsert = False)



# Execution
tt = Tagging_DB()
isbn_list = tt.collection_review.distinct("ISBN")
for row in isbn_list:
    tt.make_pos_DB(row)
# pprint(tt.pos_by_ISBN(9788997092772))
# print(isbn_list[1])
# tt.make_pos_DB(isbn_list[1])
