#-*- coding: utf-8 -*-
from pymongo import MongoClient
from konlpy.utils import pprint
import math
import operator

class TRFM:
    def __init__(self):
        client = MongoClient("110.34.84.101", 3100)
        db = client.crawl_naver_cat5
        self.collection = db.point_percent_economy
        self.collection_idf = db.point_idf_economy


    def make_trfm(self,keyword):
        trfm_list = [] #trfm을 받는 리스트
        keyword = unicode(keyword,'utf-8') #str -> unicode
        find_tag = 'tag_percent.'+keyword #mongodb 명령어 규칙을 따름
        try:
            idf_value = self.collection_idf.find({})[0][keyword]
        except KeyError:
            print("해당 태그어를 가진 책이 없습니다.")

        for col in self.collection.find({find_tag: {'$exists': 'true'}}):
            #검색한 단어가 존재하면 불러옴
            t_value = (idf_value * (col['tag_percent'][keyword]))
            #0.01은 %를 소수로 만들기 위함
            # TRFM = col['RFM']*math.log(t_value,2)
            TRFM = math.sqrt(col['RFM']) * t_value
            #TRFM 지수
            trfm_list.append([col['ISBN'],TRFM])

        dict_list = dict(trfm_list)
        #딕셔너리 타입으로 변환

        return dict_list

    def merge_trfm(self,trfm1,trfm2):
        key_trfm2 = trfm2.keys() #추가 태그어의 ISBN을 뽑음

        for key in key_trfm2:
            if(key in trfm1): #새로운 리스트의 ISBN이 기존 리스트에 있으면
                trfm1[key] = trfm1[key] + trfm2[key]
            else: #없으면 기존 리스트에 새롭게 추가
                trfm1[key] = trfm2[key]

        return trfm1 #합쳐진 리스트 반환

    def sort_trfm(self, trfm):
        #딕셔너리 타입은 순서가 없으므로 내림차순 정렬을 시켜준다
        sorted_trfm = sorted(trfm.items(), key=operator.itemgetter(1), reverse=True)

        return sorted_trfm #반환형은 list type

    def display_books(self, recommend_list): #추천 책들을 출력
        for row in recommend_list[:10]:
            bookinfo = self.collection.find_one({"ISBN": row[0]}, {"_id":0, "RFM":0, "ISBN":0, "tag_percent":0})
            print('='*50)
            pprint(bookinfo)
            print('Total TRFM: ' + str(row[1]))

        print('='*50)



#Run
tt=TRFM()

recommend_list = []
recommend_list = dict(recommend_list)
while(True):
    keyword = input("Type your Keyword: ")
    new_list = tt.make_trfm(keyword)
    merged_list = tt.merge_trfm(recommend_list, new_list)
    sorted_list = tt.sort_trfm(merged_list)
    tt.display_books(sorted_list)

#
# trfm_list 내림차순으로정렬한다음 isbn 다시 책이름및 저자 이런거검색하고 trfm랑함께 출력해주면 끝
