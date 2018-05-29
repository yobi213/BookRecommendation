import numpy as np
from pymongo import MongoClient
from nltk.probability import FreqDist

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

client = MongoClient("110.34.84.101", 3100)
db = client.crawl_naver_cat5
collection = db.point_percent_economy

data = collection.find({"ISBN": "9791186560204"}, {"_id":0, "tag_percent":1})
print(data[0]['tag_percent'])

data_fd = FreqDist(data[0]['tag_percent'])
print(data_fd.items()[:10])

data_fd.plot(50, cumulative= True)