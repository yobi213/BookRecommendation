#-*- coding: utf-8 -*-
from pymongo import MongoClient
import datetime

from konlpy.tag import Mecab
from konlpy.utils import pprint
from collections import Counter
from bson.objectid import ObjectId
import pymongo
import pytagcloud

class RFM:

    def __init__(self):
        client = MongoClient("110.34.84.101", 3100)
        db_rfm = client.crawl_naver_cat5
        self.collection_review = db_rfm.point_reviews_economy
        self.collection_rfm = db_rfm.point_rfm_economy

    def make_rm(self, isbn):
        FIRST = 1.3
        SECOND = 1.2
        THIRD =1.1
        FOURTH = 1.0
        sum_point = 0
        n = 0

        for col in self.collection_review.find({"ISBN" : isbn},{"_id" : 0, "review_date" : 1, "review_point" : 1}):
            datestr = str(col['review_date'])
            r_point = int(col['review_point'])
            time1 = datetime.datetime.strptime(datestr, "%Y.%m.%d").date()
            dist_day = datetime.date.today()-time1

            if(dist_day.days < 30):
                rm_point = r_point * FIRST
            elif((dist_day.days>=30)&(dist_day.days<90)):
                rm_point = r_point * SECOND
            elif((dist_day.days>=90)&(dist_day.days<365)):
                rm_point = r_point * THIRD
            elif(dist_day.days>=365):
                rm_point = r_point * FOURTH

            sum_point += rm_point
            n += 1


        avg_point = (sum_point)/n
        return avg_point

    def make_quarter(self, isbn):  # 기준 분위수를 얻어내기 위한 함수
        isbn_list = []  # 받아내는 ISBN 리스트를 받아낼 리스트
        isbn_list = isbn_list + isbn
        review_freq = []  # 리뷰의 개수들을 받아내는 리스트

        for row in isbn_list:
            review_freq.append(self.collection_review.find({"ISBN": row}).count())
            # 리뷰의 개수를 리스트에 하나씩 넣음

        review_freq.sort()  # 크기순으로 정렬
        print(review_freq)
        quarter = len(review_freq) / 4  # index를 4등분하여 사분위를 만든다
        self.first_quarter = review_freq[(quarter * 3) - 1]  # 1Q
        self.second_quarter = review_freq[(quarter * 2) - 1]  # 2Q
        self.third_quarter = review_freq[quarter - 1]  # 3Q

        print('=' * 50)
        print(self.first_quarter)
        print(self.second_quarter)
        print(self.third_quarter)
        print('=' * 50)

    def make_freq_point(self, isbn):  # 빈도수에 대해서 점수를 매긴다
        FIRST = 1.3
        SECOND = 1.2
        THIRD = 1.1
        FOURTH = 1.0

        # 리뷰의 개수를 얻어낸다
        review_freq = self.collection_review.find({"ISBN": isbn}).count()

        # 얻어낸 분위수를 기준으로 하여 점수를 매긴다
        if (review_freq >= self.first_quarter):
            return FIRST
        elif ((review_freq < self.first_quarter) & (review_freq >= self.second_quarter)):
            return SECOND
        elif ((review_freq < self.second_quarter) & (review_freq >= self.third_quarter)):
            return THIRD
        elif ((review_freq < self.third_quarter)):
            return FOURTH

    def make_RFM_DB(self, isbn):
        bookinfo = self.collection_review.find_one({"ISBN": isbn},
                                                   {"_id": 0, "review_text": 0, "review_date" : 0, "review_point" : 0})
        self.collection_rfm.insert(bookinfo)
        rfm = self.make_rm(isbn) * self.make_freq_point(isbn)
        self.collection_rfm.update({"ISBN": isbn}, {"$set": {"RFM": rfm}})

#Test

tt=RFM()
isbn_list = tt.collection_review.distinct("ISBN")
tt.make_quarter(isbn_list)

for row in isbn_list:
    tt.make_RFM_DB(row)

# tt.make_rm("9791186560204")