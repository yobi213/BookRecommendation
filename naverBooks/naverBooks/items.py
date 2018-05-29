# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class NaverbooksItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field() # 책 제목
    author = scrapy.Field() # 책 저자
    ISBN = scrapy.Field() # ISBN
    category = scrapy.Field() # 장르
    publisher = scrapy.Field() # 출판사
    publish_date = scrapy.Field() # 출판일
    review_point = scrapy.Field() # 리뷰 점수
    review_date = scrapy.Field() # 리뷰 등록 날짜
    review_text = scrapy.Field() # 리뷰 내용
    page = scrapy.Field()
    bid = scrapy.Field()
    pass

