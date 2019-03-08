import scrapy
import json
import re
import mysql.connector
import datetime
from .database import Database

class FaceToFace(scrapy.Spider):
    name = "facetofaceafrica"
    countries = [
        'nigerias',
        'cameroons'
         ]

    def start_requests(self):
        urls = [
            "https://face2faceafrica.com/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        links_crawled = []
        page = response.url.split("/")[-2]
        filename = 'urls-%s.txt' % page
        f = open(filename, 'w')
        f.write(response.text)
        for articles in response.css("ul#top-stories"):
            url = articles.css("li > a::attr(href)").get()
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
        article = response.css("div.column--primary")

        url = response.url
        img = article.css("figure span img::attr(src)").get()
        title = self.clean_string(article.css("h1.story-body__h1::text").get())
        date = self.clean_string(article.css("div.date::text").get())
        excerpt = article.css("p.story-body__introduction::text").get()
        page = response.url.split("/")[-3]
        insert_time = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        
        db = Database(url, img, title, excerpt, date, page, insert_time)
        
        for country in self.countries:
            db.fill_db(country)
        self.log('Saved data into DATABASE SUCCESS')
        
    def clean_string(self, mystring):
        return re.sub('[\t\r\n]+', '', mystring)