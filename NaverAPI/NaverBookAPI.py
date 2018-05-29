# -*- coding : UTF-8 -*-
#python 3.0 이상에서 실행해야 아무런 오류 없이 실행이 된다.

import os
import sys
import urllib.request
from xml.etree.ElementTree import fromstring
import csv



#NaverAPI를 이용하여 책의 링크를 얻어오도록 한다.
class NaverAPI:
    def __init__(self):
        pass

    def setdata(self, data):
        self.isbn_list = []
        f = open('./%s' % data, 'r')
        csvReader = csv.reader(f)

        for row in csvReader:
            self.isbn_list.append(row)

        f.close()

    def search_link(self, isbn):
        #네이버 API를 이용해서 책의 링크를 불러온다.
        client_id = "SDHY_kv52NVJ4FbAq6GS"
        client_secret = "YiO1R2VVrp"
        encText = urllib.parse.quote(str(isbn))
        url = "https://openapi.naver.com/v1/search/book_adv.xml?d_isbn=" + encText

        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id",client_id)
        request.add_header("X-Naver-Client-Secret",client_secret)
        response = urllib.request.urlopen(request)
        rescode = response.getcode()
        if(rescode==200):

            response_body = response.read()
            target_xml = response_body.decode('utf-8')
            #불러들인 xml내용은 string 타입으로 저장되어 있다. 그래서 fromstring을 이용하여 파싱한다.
            root = fromstring(target_xml)
            #파싱을 한 것에서 링크를 찾아 내어 text 형태로 저장한다.
            bid = root[0][7][1].text.split("=")[1]
            f = open('./bid_list.csv', 'a', encoding='UTF-8')
            #bid만 저장
            #모든 네이버의 책이 bid의 개수가 8개인지 확인해야 한다.
            csvWriter = csv.writer(f)

            csvWriter.writerow([str(bid)])
            f.close()
            print(root[0][7][1].text.split("=")[1])

        else:
            print("Error Code:" + rescode)

    def all_search(self):
        for i in self.isbn_list:
            self.search_link(i)




# Test
a = NaverAPI()
a.setdata('aladin_isbn_list2.csv')
a.all_search()