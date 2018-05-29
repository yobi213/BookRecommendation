# -*- coding: utf-8 -*-

from pymongo import MongoClient
import operator

class Extract_Tag:
    def __init__(self):
        client = MongoClient("110.34.84.101", 3100)
        db_cat5 = client.crawl_naver_cat5
        # 불러오는 raw_collection
        self.collection_tag = db_cat5.tag_reviews_economy
        # 불러오는 rfm_collection
        self.collection_rfm = db_cat5.point_rfm_economy
        # 저장하는 collection
        self.collection_percent = db_cat5.point_percent_economy


    def make_TF_percent(self,isbn):

        raw_tag = self.collection_tag.find({"ISBN": isbn}, {"_id": 0, "tag": 1})
        dict_tag = raw_tag[0]['tag']
        sum = 0

        for n in dict_tag.values():
            #책에 있는 모든 단어의 카운트 수 추출 후 합
            sum += n

        sorted_tag = sorted(dict_tag.items(), key=operator.itemgetter(1), reverse=True)
        percent_tag =[]
        for row in sorted_tag:
            percent_tag.append([row[0], row[1]*1.0/sum*100, row[1]])

        cum_percent = 0
        fifty_tag = []
        for row in percent_tag:
            cum_percent += row[1]
            fifty_tag.append([row[0], row[1], row[2]])
            if(cum_percent>=50):
                break

        fifty_sum = 0
        for row in fifty_tag:
            fifty_sum += row[2]

        final_tag = []
        for row in fifty_tag:
            final_tag.append([row[0], row[2]*1.0/fifty_sum*100])

        tag_key = []
        tag_value = []
        for row in final_tag:
            tag_key.append(row[0])
            tag_value.append(row[1])

        fifty_zip_tag = zip(tag_key, tag_value)
        fifty_dict_tag = dict(fifty_zip_tag)

        return fifty_dict_tag

    def make_percent_DB (self, isbn):
        bookinfo = self.collection_rfm.find_one({"ISBN" : isbn}, {"_id": 0})

        try:
            self.collection_percent.insert(bookinfo)
            self.collection_percent.update({"ISBN": isbn}, {"$set": {"tag_percent": self.make_TF_percent(isbn)}},
                                           upsert=False)
        except TypeError:
            print("No RFM in DB")

        print(isbn + " save completely")



#Execution
tt = Extract_Tag()
isbn_list = tt.collection_tag.distinct("ISBN")
for isbn in isbn_list:
    tt.make_percent_DB(isbn)

