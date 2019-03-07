import scrapy
import json
import re
import mysql.connector
import datetime
from .database import Database


class TheGuardian(scrapy.Spider):
    name = "theguardian"
    table = "austrailias"
    
    def start_requests(self):
        urls = [
            'https://www.theguardian.com/au',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        links_crawled = []
        page = response.url.split("/")[-2]
        filename = 'urls-%s.txt' % page
        f = open(filename, 'w')

        for articles in response.css("div.fc-item__container"):
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
        article = response.css("div.gs-container")
        print(response)
        url = response.url
        image = article.css("figure.media-primary a picture img::attr(src)").get()
        title = self.clean_string(article.css("h1.content__headline::text").get())
        excerpt = article.css("div.content__article-body p::text").get()
        date = self.clean_string(article.css("p.content__dateline time::attr(datetime)").get())
        page = response.url.split("/")[2]
        insert_time = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())

        db = Database(url, image, title, excerpt, date, page, insert_time)
        db.fil_db(self.table)

        self.log('Saved data into DATABASE SUCCESS')
        
    def clean_string(self, mystring):
        return re.sub('[\t\r\n]+', '', mystring)
    