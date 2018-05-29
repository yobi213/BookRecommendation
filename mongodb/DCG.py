#-*- coding: utf-8 -*-
from pymongo import MongoClient
from konlpy.utils import pprint
import operator
import math


class DCG:
    def __init__(self):
        client = MongoClient("110.34.84.101", 3100)
        db = client.crawl_naver_cat5
        self.collection = db.point_percent_economy
        self.collection_idf = db.point_idf_economy

        self.rfm_dict = []
        self.rfm_dict = dict(self.rfm_dict)

    def make_trfm(self, keyword, mode):
        trfm_list = [] #trfm을 받는 리스트
        keyword = unicode(keyword,'utf-8') #str -> unicode
        find_tag = 'tag_percent.'+keyword #mongodb 명령어 규칙을 따름

        try:
            idf_value = self.collection_idf.find({})[0][keyword]
        except KeyError:
            print("해당 태그어를 가진 책이 없습니다.")

        for col in self.collection.find({find_tag: {'$exists': 'true'}}):
            #검색한 단어가 존재하면 불러옴
            t_value = idf_value * (col['tag_percent'][keyword])
            #0.01은 %를 소수로 만들기 위함
            # if(mode==1): TRFM = col['RFM']**t_value
            if (mode == 1): TRFM = col['RFM']*math.log(t_value,2)
            elif(mode==2): TRFM = col['RFM']*math.sqrt(t_value)
            # elif(mode==3): TRFM = col['RFM']*t_value
            # elif(mode==4): TRFM = col['RFM']*math.sqrt(t_value)
            # elif (mode == 5): TRFM = col['RFM'] * (1 + (math.log(t_value,2)))
            # elif (mode == 6): TRFM = col['RFM'] * (math.log(t_value, 2))


            #TRFM 지수
            trfm_list.append([col['ISBN'],TRFM])

            self.rfm_dict[col['ISBN']] = col['RFM']

        dict_list = dict(trfm_list)
        #딕셔너리 타입으로 변환

        return dict_list

    def merge_trfm(self, trfm1, trfm2):
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

#==================================================================================================
#DCG


    def make_dcg(self, keyword):
        rel_list = [] #rel을 받는 리스트
        keyword = unicode(keyword,'utf-8') #str -> unicode
        find_tag = 'tag_percent.'+keyword #mongodb 명령어 규칙을 따름

        try:
            idf_value = self.collection_idf.find({})[0][keyword]
        except KeyError:
            print("해당 태그어를 가진 책이 없습니다.")

        for col in self.collection.find({find_tag: {'$exists': 'true'}}):
            #검색한 단어가 존재하면 불러옴
            dcg_rel = (idf_value * (col['tag_percent'][keyword])) #scale : X100
            rel_list.append([col['ISBN'],dcg_rel])

        dict_list = dict(rel_list)
        #딕셔너리 타입으로 변환

        return dict_list

    def merge_rel(self, rel1, rel2):
        key_rel2 = rel2.keys() #추가 태그어의 ISBN을 뽑음

        for key in key_rel2:
            if(key in rel1): #새로운 리스트의 ISBN이 기존 리스트에 있으면
                rel1[key] = rel1[key] + rel2[key]
            else: #없으면 기존 리스트에 새롭게 추가
                rel1[key] = rel2[key]

        return rel1 #합쳐진 dict 반환

    def calc_DCG(self, rel_list, recommend_list):
        rel = []
        for row in recommend_list[:10]:
            rel.append(rel_list[str(row[0])])

        dcg_score = 0

        for i in xrange(len(rel)):
            dcg_score += rel[i]/math.log((i+1)+1, 2)

        return dcg_score

    def var_TRFM(self, recommend_list):
        sum_trfm = 0

        for row in recommend_list[:10]:
            sum_trfm += row[1]

        avg_trfm = sum_trfm/10

        temp = 0
        for row in recommend_list[:10]:
            temp += (row[1]-avg_trfm)**2

        var_trfm = temp/10

        return var_trfm


    def display_books(self, recommend_list, rel_list):  # 추천 책들을 출력
        rfm_total = 0

        for i in xrange(10):
            isbn = recommend_list[i][0]
            rfm_total += self.rfm_dict[isbn]
            bookinfo = self.collection.find_one({"ISBN": recommend_list[i][0]}, {"_id": 0, "title": 1})
            print('=' * 50)
            pprint(bookinfo)
            # print('ISBN:' + str(isbn))
            print('Tag Point:' + str(rel_list[isbn]))
            print('Total TRFM: ' + str(recommend_list[i][1]))

        print('=' * 50)
        print('*'*5 + "Total RFM: " + str(rfm_total) + "*"*5)

    def display_models(self, recommend_list, rel_list):  # 추천 책들을 출력
        rfm_total = 0

        for i in xrange(10):
            isbn = recommend_list[i][0]
            rfm_total += self.rfm_dict[isbn]


        print('=' * 50)
        print("DCG: " + str(self.calc_DCG(rel_list, recommend_list)))
        print("Total RFM: " + str(rfm_total))
        print("Var(TRFM): " + str(self.var_TRFM(recommend_list)))


    def run_test(self, keyword, mode, recommend_list, rel_list):
        new_list = tt.make_trfm(keyword, mode)
        merged_list = tt.merge_trfm(recommend_list, new_list)
        sorted_list = tt.sort_trfm(merged_list)

        new_rel_list = tt.make_dcg(keyword)
        merged_rel_list = tt.merge_rel(rel_list, new_rel_list)
        # dcg_score = tt.calc_DCG(merged_rel_list, sorted_list)

        # tt.display_books(sorted_list, merged_rel_list)
        print("*"*10 + " Mode :" + str(mode) +" "+ "*"*10)
        tt.display_models(sorted_list, merged_rel_list)
        # print("DCG: " + str(dcg_score))



#Run
tt=DCG()

# recommend_list1 = []
# recommend_list1 = dict(recommend_list1)
# rel_list1 = []
# rel_list1 = dict(rel_list1)
# recommend_list2 = []
# recommend_list2 = dict(recommend_list2)
# rel_list2 = []
# rel_list2 = dict(rel_list2)
# recommend_list3 = []
# recommend_list3 = dict(recommend_list3)
# rel_list3 = []
# rel_list3 = dict(rel_list3)
# recommend_list4 = []
# recommend_list4 = dict(recommend_list4)
# rel_list4 = []
# rel_list4 = dict(rel_list4)

while(True):
    keyword = input("Type your Keyword: ")

    for i in xrange(1, 3):
        recommend_list1 = []
        recommend_list1 = dict(recommend_list1)
        rel_list1 = []
        rel_list1 = dict(rel_list1)
        tt.run_test(keyword, i, recommend_list1, rel_list1)




    # new_list = tt.make_trfm(keyword,4)
    # merged_list = tt.merge_trfm(recommend_list, new_list)
    # sorted_list = tt.sort_trfm(merged_list)
    #
    # new_rel_list = tt.make_dcg(keyword)
    # merged_rel_list = tt.merge_rel(rel_list, new_rel_list)
    # dcg_score = tt.calc_DCG(merged_rel_list, sorted_list)
    #
    # # tt.display_books(sorted_list, merged_rel_list)
    # tt.display_models(sorted_list, merged_rel_list)
    # print("*"*5 +"DCG: "+ str(dcg_score) +"*"*5)