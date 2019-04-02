import scrapy
import json
import re
import mysql.connector
import datetime
from .database import Database

class PunchNG(scrapy.Spider):
    name = "punchng"
    table = "nigerias"

    def start_requests(self):
        urls = [
            'https://punchng.com/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        links_crawled = []
        page = response.url.split("/")[-2]
        filename = 'urls-%s.txt' % page
        f = open(filename, 'w')

        for articles in response.css("div.latest-news ul li"):
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
        article = response.css("main.site-main")
        f.write(response.url)
        f.write(response.text)
        url = response.url
        img = article.css("div.entry-content img::attr(src)").get()
        title = self.clean_string(article.css("h1.post_title::text").get())
        # date = self.clean_string(article.css("span.timestamp::text").get())
        excerpt = article.css("div.entry-content p::text").get()
        page = response.url.split("/")[2]
        insert_time = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        
        db = Database(url, img, title, excerpt, insert_time, page, insert_time)
        db.fill_db(self.table)

        self.log('Saved data into DATABASE SUCCESS')
        
    def clean_string(self, mystring):
        return re.sub('[\t\r\n]+', '', mystring)
       