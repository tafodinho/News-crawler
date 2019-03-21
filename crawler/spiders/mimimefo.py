import scrapy
import json
import re
import mysql.connector
import datetime
from .database import Database


class MimiMefo(scrapy.Spider):
    name = "mimimefo"
    table = "cameroons"
    
    def start_requests(self):
        urls = [
            'https://mimimefoinfos.com/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        links_crawled = []
        page = response.url.split("/")[-2]
        filename = 'urls-%s.txt' % page
        f = open(filename, 'w')

        for articles in response.css("article"):
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
        article = response.css("article.post")
        print(response)
        url = response.url
        image = article.css(".entry-media img::attr(src)").get()
        title = self.clean_string(article.css("header h1::text").get())
        excerpt = article.css(".entry-content p::text").getall()[2]
        date = self.clean_string(article.css("header time::attr(datetime)").get())
        page = response.url.split("/")[2]
        insert_time = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

        db = Database(url, image, title, excerpt, date, page, insert_time)
        db.fill_db(self.table)

        self.log('Saved data into DATABASE SUCCESS')
        
    def clean_string(self, mystring):
        return re.sub('[\t\r\n]+', '', mystring)
    