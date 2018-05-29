#-*- coding: utf-8 -*-

from pymongo import MongoClient
from konlpy.utils import pprint
import numpy as np
from collections import namedtuple
from gensim.models import doc2vec

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class PredPoint():
    def __init__(self):
        client = MongoClient("110.34.84.101", 3100)
        db = client.crawl_naver_cat5
        self.collection = db.words_reviews_economy

    def read_good_data(self):
        data = self.collection.aggregate([{"$match": {"$or": [{"review_point": "10"},
                                                              {"review_point": "9"}]}}, {"$sample": {"size": 500}}])
        data_list = []

        for row in data:
            w = []
            for row2 in row['words']:
                w.append(row2[0] + '/' + row2[1])

            data_list.append((w, 1))

        # pprint(data_list)

        return data_list

    def read_bad_data(self):
        data = self.collection.aggregate([{"$match": {"$or": [{"review_point": "1"},
                                                              {"review_point": "2"},
                                                              {"review_point": "3"},
                                                              {"review_point": "4"}]}},
                                          {"$sample": {"size": 500}}])
        data_list = []

        for row in data:
            w = []
            for row2 in row['words']:
                w.append(row2[0] + '/' + row2[1])

            # print(row['review_point'])
            data_list.append((w, 0))

        # pprint(data_list)

        return data_list


#Run
knock = PredPoint()
good_data = knock.read_good_data()
# print(len(good_data))
bad_data = knock.read_bad_data()
# print(len(bad_data))

good_array = np.array(good_data)
bad_array = np.array(bad_data)

#making sampling index
x = np.random.rand(492,1)
training_idx = np.random.randint(x.shape[0], size=400)
test_idx = np.random.randint(x.shape[0], size=92)

#making training set and test set
training_good, test_good = good_array[training_idx,:], good_array[test_idx,:]
training_bad, test_bad = bad_array[training_idx,:], bad_array[test_idx,:]
#concatenate good and bad
train_docs = np.concatenate((training_good, training_bad), axis=0)
test_docs = np.concatenate((test_good, test_bad), axis=0)

#Doc2vec
TaggedDocument = namedtuple('TaggedDocument', 'words tags')
tagged_train_docs = [TaggedDocument(d, [c]) for d, c in train_docs]
tagged_test_docs = [TaggedDocument(d, [c]) for d, c in test_docs]


# 사전 구축
doc_vectorizer = doc2vec.Doc2Vec(size=500, alpha=0.025, min_alpha=0.025, seed=1234)
doc_vectorizer.build_vocab(tagged_train_docs)
print(len(tagged_train_docs))
# Train document vectors!
for epoch in range(10):
    doc_vectorizer.train(tagged_train_docs, 400, epochs=epoch)
    doc_vectorizer.alpha -= 0.002  # decrease the learning rate
    doc_vectorizer.min_alpha = doc_vectorizer.alpha  # fix the learning rate, no decay

pprint(doc_vectorizer.most_similar([u'산업/NNG']))

train_x = [doc_vectorizer.infer_vector(doc.words) for doc in tagged_train_docs]
train_y = [doc.tags[0] for doc in tagged_train_docs]
print(len(train_x))
# 사실 이 때문에 앞의 term existance와는 공평한 비교는 아닐 수 있다
# => 150000
print(len(train_x[0]))
# => 300
test_x = [doc_vectorizer.infer_vector(doc.words) for doc in tagged_test_docs]
test_y = [doc.tags[0] for doc in tagged_test_docs]
print(len(test_x))
# => 50000
print(len(test_x[0]))
# => 300

from sklearn.linear_model import LogisticRegression
classifier = LogisticRegression(random_state=1234)
classifier.fit(train_x, train_y)
print(classifier.score(test_x, test_y))

# print(classifier.predict_proba(test_x[0].reshape(-1,1)))