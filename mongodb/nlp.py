#-*- coding: utf-8 -*-
from pymongo import MongoClient
from konlpy.tag import Mecab
from konlpy.utils import pprint
from collections import Counter
from bson.objectid import ObjectId
from konlpy.utils import pprint
import pymongo
import pytagcloud

import operator
#
# client = MongoClient("110.34.84.101", 3100)
# db = client.crawl_naver_cat5
# collection = db.tag_reviews_economy
#
# col = collection.find({"ISBN" : "9791186560204"},{"_id" :0, "tag": 1})
#
# col = collection.find({'tag.낱말': {'$ne' : 'null'}})

class TRFM:
    def __init__(self):
        client = MongoClient("110.34.84.101", 3100)
        db = client.crawl_naver_cat5
        self.collection = db.point_percent_economy

    def make_trfm(self,keyword):
        trfm_list = []
        keyword = unicode(keyword,'utf-8')
        find_tag = 'tag_percent.'+keyword
        for col in self.collection.find({find_tag: {'$exists': 'true'}}):
            t_value = 1 + (col['tag_percent'][keyword]*0.01)
            TRFM = col['RFM']**t_value
            trfm_list.append([col['ISBN'],TRFM])
        return trfm_list



tt=TRFM()
list = tt.make_trfm('산업')

# tt.make_tagvalue('낱말') + tt.make_tagvalue('혁명')
#
# trfm_list 내림차순으로정렬한다음 isbn 다시 책이름및 저자 이런거검색하고 trfm이랑함께 출력해주면 끝

# collection_test.find({ "title" : "주진우의 이명박 추격기"})
# collection_test.update( { "title" : "주진우의 이명박 추격기"}, { $review_text: {"title" : "이명박"} } )


# collection_test.update(
# ,"reviews_pos" : '단어/형태')

# mecab = Mecab()
# nouns = mecab.nouns(a)
# count = Counter(nouns)
# count.most_common(10)
# tag2 = count.most_common(40)
# taglist = pytagcloud.make_tags(tag2, maxsize=80)
#
# pytagcloud.create_tag_image(taglist, 'wordcloud.jpg', size=(900, 600), fontname='Korean', rectangular=False)