import scrapy
import json
import re
import mysql.connector
import datetime
from .database import Database

class ABCNews(scrapy.Spider):
    name = "abcnews"
    table = "austrailias"

    def start_requests(self):
        urls = [
            'https://www.abc.net.au/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        links_crawled = []
        page = response.url.split("/")[-2]
        filename = 'urls-%s.txt' % page
        f = open(filename, 'w')

        for articles in response.css(".article"):
            url = articles.css("a::attr(href)").get()
            if url[0] is '/':
                url = response.url[:-1] + url
            if url in links_crawled:
                continue
            try:
                f.write(json.dumps({'url': url}))
                f.write('\n')
                links_crawled.append(url)
                yield scrapy.Request(url=url, callback=self.parse1)
            except:
                pass
        
        self.log('Saved file %s' % filename)
        f.close()

    def parse1(self, response):
        f = open("abctesting.txt", "w")
        article = response.css("div.article")
        f.write(response.url)
        f.write(response.text)
        url = response.url
        img = article.css("div.photo img::attr(src)").get()
        title = self.clean_string(article.css("h1::text").get())
        date = self.clean_string(article.css("span.timestamp::text").get())
        excerpt = article.css("p::text").getall()[2]
        page = response.url.split("/")[2]
        insert_time = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        
        db = Database(url, img, title, excerpt, date, page, insert_time)
        db.fill_db(self.table)

        self.log('Saved data into DATABASE SUCCESS')
        
    def clean_string(self, mystring):
        return re.sub('[\t\r\n]+', '', mystring)
       