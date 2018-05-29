# -*- coding: utf-8 -*-
from pymongo import MongoClient
from konlpy.tag import Mecab
from konlpy.utils import pprint
from collections import Counter
import pytagcloud

class Tagging_DB:
    def __init__(self):
        client = MongoClient("110.34.84.101", 3100)
        db_review = client.books_crawl
        self.collection_review = db_review.reviews
        db_tag = client.books_tag
        self.collection_TitleTag = db_tag.TagPerTitle
        self.collection_CategoryTag = db_tag.TagPerCategory

    def make_tag_category (self, contents):
        mecab = Mecab()
        tmp_tag = []
        count = Counter(' ')

        for col in self.collection_review.find({"category" : contents},{"_id" : 0, "review_text" : 1}):
            pos = mecab.pos(col['review_text'])

            for i in xrange(1, len(pos), 1):
                if (pos[i][1] == "NNG") | (pos[i][1] == "NNP"):
                    print pos[i][0]
                    tmp_tag.append(pos[i][0])

            count = count + Counter(tmp_tag)
            print type(count)

        tag = count.most_common(200)
        self.collection_CategoryTag.insert({"category": contents, "tag": tag})

        return tag


    def make_tag_title (self, contents):
        mecab = Mecab()
        tmp_tag = []
        count = Counter(' ')

        for col in self.collection_review.find({"title": contents}, {"_id": 0, "review_text": 1}):
            pos = mecab.pos(col['review_text'])

            for i in xrange(1, len(pos), 1):
                if (pos[i][1] == "NNG") | (pos[i][1] == "NNP"):
                    print pos[i][0]
                    tmp_tag.append(pos[i][0])

            count = count + Counter(tmp_tag)
            print type(count)

        tag = count.most_common(100)
        self.collection_TitleTag.insert({"title": contents, "tag": tag})

        return tag

    def draw_wordcloud(self, tag, name):
        taglist = pytagcloud.make_tags(tag, maxsize=80)
        pytagcloud.create_tag_image(taglist, '%s.jpg' % name, size=(900, 600), fontname='Korean', rectangular=False)

    def insert_tag_title(self):
        self.collection_tag.insert({"title" : self.title, "nouns": tag})

    def insert_tag_category(self):
        self.collection_tag.insert({"category": self.title, "nouns": tag})



# Execution
tt = Tagging_DB()
# allTitle = tt.collection_review.distinct("title")
# for title in allTitle :
#     tt.make_tag_title(title)

category_tag = tt.make_tag_category("사회")

tt.draw_wordcloud(category_tag, "category_wordcloud")

title_tag = tt.make_tag_title("나의 문화유산답사기 ")
tt.draw_wordcloud(title_tag, "title_wordcloud")
