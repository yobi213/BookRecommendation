# -*- coding: utf-8 -*-
from pymongo import MongoClient
from konlpy.tag import Mecab
from collections import Counter
from konlpy.utils import pprint


class Tagging_DB:
    def __init__(self):
        client = MongoClient("110.34.84.101", 3100)
        db_review = client.crawl_naver_cat5
        #불러오는 raw_collection
        self.collection_review = db_review.raw_reviews_develop
        #저장하는 pos collection
        db_pos = client.crawl_naver_cat5
        self.collection_pos = db_pos.tag_reviews_develop


    def make_tag_DB (self, contents):
        bookinfo = self.collection_review.find_one({"ISBN" : contents}, {"_id" : 0, "review_text" : 0})
        self.collection_pos.insert(bookinfo)
        tag = self.make_tag(contents)
        self.collection_pos.update({"ISBN": contents}, {"$set" : {"tag" : tag}})
        # self.collection_pos.update({"title": contents}, {"$set" : {"reviews_pos" : self.pos_by_ISBN(contents)}}, upsert = False)


    def make_tag(self, contents):
        mecab = Mecab()
        tmp_tag = []
        count = Counter(' ')

        for col in self.collection_review.find({"ISBN": contents}, {"_id": 0, "review_text": 1}):
            pos = mecab.pos(col['review_text'])

            for i in xrange(1, len(pos), 1):
                if (pos[i][1] == "NNG") | (pos[i][1] == "NNP"):
                    print pos[i][0]
                    tmp_tag.append(pos[i][0])

            count = count + Counter(tmp_tag)
            print type(count)

        tag = count
        # self.collection_TitleTag.insert({"ISBN": contents, "tag": tag})

        return tag


# Execution
tt = Tagging_DB()
isbn_list = tt.collection_review.distinct("ISBN")
for row in isbn_list:
    tt.make_tag_DB(row)
# pprint(tt.pos_by_ISBN(9788997092772))
# print(isbn_list[1])
# tt.make_pos_DB(isbn_list[1])
