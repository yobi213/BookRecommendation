#-*- coding: utf-8 -*-

import DCG
from pymongo import MongoClient
from konlpy.utils import pprint
import numpy as np

#Access mongoDB
client = MongoClient("110.34.84.101", 3100)
db = client.crawl_naver_cat5
collection_idf = db.point_idf_economy

signal = DCG.DCG()

data = collection_idf.find_one()
keys = data.keys()
new_data = []
for row in keys:
    if (data[row] < 2)&(data[row]!=0) :
        new_data.append(row)

# print(new_data)
keys_arr = np.array(new_data)

print(len(keys_arr))
sample_keys = np.random.choice(keys_arr, 200, replace=False)
pprint(sample_keys)

for row in sample_keys:
    keyword = row

    for mode in xrange(1, 5):
        recommend_list1 = []
        recommend_list1 = dict(recommend_list1)
        rel_list1 = []
        rel_list1 = dict(rel_list1)
        signal.run_test(keyword, mode, recommend_list1, rel_list1)