import scrapy
import json
import re
import mysql.connector
import datetime
from .database import Database

class UNOrg(scrapy.Spider):
    name = "unorg"
    countries = [
        'cameroons', 
        'austrailias'
    ]

    def start_requests(self):
        urls = [
            "https://news.un.org/en/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        links_crawled = []
        page = response.url.split("/")[-2]
        filename = 'urls-%s.txt' % page
        f = open(filename, 'w')
        # f.write(response.text)
        for articles in response.css(".featured-media"):
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
        article = response.css("div.main-container")

        url = response.url
        img = article.css(".featured-media picture img::attr(src)").get()
        title = self.clean_string(article.css("h1.story-title::text").get())
        # date = self.clean_string(article.css(".jeg_meta_date a::text").get())
        excerpt = article.css(".field-item p::text").get()
        page = response.url.split("/")[-3]
        insert_time = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        
        db = Database(url, img, title, excerpt, insert_time, page, insert_time)
        
        for country in self.countries:
            db.fill_db(country)
        
        self.log('Saved data into DATABASE SUCCESS')
        
    def clean_string(self, mystring):
        return re.sub('[\t\r\n]+', '', mystring)