import scrapy
import json
import re
import mysql.connector
import datetime
from .database import Database

class USAToday(scrapy.Spider):
    name = "usatoday"
    table = "americas"

    def start_requests(self):
        urls = [
            'https://usatoday.com/',
        ]
        for url in urls:
            yield scrapy.Request(url=url,
             meta = {
                      'dont_redirect': True
            },
            callback=self.parse)

    def parse(self, response):
        links_crawled = []
        page = response.url.split("/")[-2]
        filename = 'urls-%s.txt' % page
        f = open(filename, 'w')

        for articles in response.css("li.hfwmm-item"):
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
        article = response.css("article")
        f.write(response.url)
        f.write(response.text)
        url = response.url
        img = article.css("div.asset-double-wide img::attr(src)").get()
        title = self.clean_string(article.css("section.storytopbar-bucket h1::text").get())
        # date = self.clean_string(article.css("span.timestamp::text").get())
        excerpt = article.css("div.asset-double-wide p::text").getall()[1]
        page = response.url.split("/")[2]
        insert_time = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        
        db = Database(url, img, title, excerpt, insert_time, page, insert_time)
        db.fill_db(self.table)

        self.log('Saved data into DATABASE SUCCESS')
        
    def clean_string(self, mystring):
        return re.sub('[\t\r\n]+', '', mystring)
       