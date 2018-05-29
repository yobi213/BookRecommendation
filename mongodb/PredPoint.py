from pymongo import MongoClient
from konlpy.utils import pprint
import nltk
import random
import numpy as np

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class PredPoint():
    def __init__(self):
        client = MongoClient("110.34.84.101", 3100)
        db = client.crawl_naver_cat5
        self.collection = db.words_reviews_economy

    def read_good_data(self):
        data = self.collection.find({"$or":[{"review_point":"10"}, {"review_point":"9"}]})
        data_list = []

        for row in data:
            w = []
            for row2 in row['words']:
                w.append(row2[0]+'/'+row2[1])

            data_list.append((w,1))

        # pprint(data_list)

        return data_list

    def read_bad_data(self):
        data = self.collection.find({"$or":[{"review_point":"1"}, {"review_point":"2"},
                                            {"review_point": "3"}, {"review_point": "4"}]})
        data_list = []

        for row in data:
            w = []
            for row2 in row['words']:
                w.append(row2[0]+'/'+row2[1])

            # print(row['review_point'])
            data_list.append((w,0))

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

tokens = [t for d in train_docs for t in d[0]]
print(len(tokens))

text = nltk.Text(tokens, name='BookReviews')
print(text)
print(len(text.tokens))
print(len(set(text.tokens)))
pprint(text.vocab().most_common(10))

nltk.download('stopwords')
text.collocations()

selected_words = [f[0] for f in text.vocab().most_common(2000)]

def term_exists(doc):
    return {'exists({})'.format(word): (word in set(doc)) for word in selected_words}

train_docs = train_docs[:800]
train_xy = [(term_exists(d), c) for d, c in train_docs]
test_xy = [(term_exists(d), c) for d, c in test_docs]

classifier = nltk.NaiveBayesClassifier.train(train_xy)
print(nltk.classify.accuracy(classifier, test_xy))

classifier.show_most_informative_features(10)