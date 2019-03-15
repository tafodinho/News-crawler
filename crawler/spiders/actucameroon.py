import scrapy
import json
import re
import mysql.connector
import datetime
from .database import Database


class ActuCameroun(scrapy.Spider):
    name = "actunews"
    table = "cameroons"
    
    def start_requests(self):
        urls = [
            'https://actucameroun.com/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        links_crawled = []
        page = response.url.split("/")[-2]
        filename = 'urls-%s.txt' % page
        f = open(filename, 'w')

        for articles in response.css(".td-block-span4"):
            url = articles.css("a::attr(href)").get()
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
        article = response.css("article")
        print(response)
        url = response.url
        image = article.css("div.td-post-featured-image img::attr(src)").get()
        title = self.clean_string(article.css("h1.entry-title::text").get())
        excerpt = article.css("div.td-post-content p::text").get()
        date = self.clean_string(article.css("time::attr(datetime)").get())
        page = response.url.split("/")[2]
        insert_time = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

        db = Database(url, image, title, excerpt, date, page, insert_time)
        db.fill_db(self.table)

        self.log('Saved data into DATABASE SUCCESS')
        
    def clean_string(self, mystring):
        return re.sub('[\t\r\n]+', '', mystring)
    