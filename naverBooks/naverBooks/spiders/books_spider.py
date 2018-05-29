# -*- coding : utf-8 -*-

import scrapy
import csv
from naverBooks.items import NaverbooksItem

class Page_Spider(scrapy.Spider):

    name = "pc"

    def start_requests(self):
        with open('/Users/mac/PycharmProjects/naverBooks/bid_list.csv') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                url = "http://book.naver.com/bookdb/review.nhn?bid=" + row[0]
                # url = "http://book.naver.com/bookdb/review.nhn?bid=12143302"
                yield scrapy.Request(url, self.parse)

    def parse(self, response):
        num = response.xpath('//*[@id="content"]/div/div[1]/span/text()').re(r'\d*\d')
        bid = response.xpath('/html/head/meta[5]').re(r'\d*\d')

        if len(num) > 1 :
            num = str(num[0]) + str(num[1])
            num = (int(num) / 10) + 1
        else :
            num = (int(num[0]) / 10) + 1

        yield {
            'page': num,
            'bid' : bid
        }


class Book_Spider(scrapy.Spider):

    name = "nb"

    def start_requests(self):
        with open('./page_list2.csv') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                pg_num = int(row['page'])
                print pg_num
                for i in range(1, pg_num+1, 1):
                    print row['page']
                    print pg_num
                    print row['bid']
                    print '8'*100
                    url = "http://book.naver.com/bookdb/review.nhn?bid={0}&page={1}".format(row['bid'], i)
                    # url = "http://book.naver.com/bookdb/review.nhn?bid=" + row[0] + "&page=%d" % i
                    yield scrapy.Request(url, self.parse)

    def parse(self, response):
        i = 1

        for book_list in response.xpath('//*[@id="reviewList"]/li'):
            item = NaverbooksItem()

            item['title'] = book_list.xpath('//*[@id="container"]/div[4]/div[1]/h2/a/text()').extract_first()
            item['author'] = book_list.xpath(
                '//*[@id="container"]/div[4]/div[1]/div[2]/div[2]/a[1]/text()').extract_first()
            # item['ISBN'] = book_list.xpath('//*[@id="container"]/div[4]/div[1]/div[2]/div[4]/text()[3]').extract_first()
            item['category'] = book_list.xpath('//*[@id="category_location1_depth"]/text()').extract_first()
            item['publisher'] = book_list.xpath(
                '//*[@id="container"]/div[4]/div[1]/div[2]/div[2]/a[2]/text()').extract_first()
            item['publish_date'] = book_list.xpath(
                '//*[@id="container"]/div[4]/div[1]/div[2]/div[2]/text()[last()]').extract_first()
            item['review_point'] = book_list.xpath('./dl/dd[@class="txt_inline"]/em/text()').extract_first()
            item['review_date'] = book_list.xpath('./dl/dd[@class="txt_inline"][last()]/text()').extract_first()
            item['review_text'] = book_list.xpath('.//dd[@id="review_text_%d"]/text()' % i).extract_first()

            if i == (len(response.xpath('//*[@id="reviewList"]/li')) + 1):
                i = 1
            else:
                i = i + 1

            # time.sleep(50)

            yield item