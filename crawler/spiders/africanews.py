import scrapy
import json
import re
import mysql.connector
import datetime
from .database import Database
class AfricaNews(scrapy.Spider):
    name = "africanews"
    countries = [
        'nigerias', 
        'cameroons'
        ]

    def start_requests(self):
        urls = [
            "https://www.africanews.com/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        links_crawled = []
        page = response.url.split("/")[-2]
        filename = 'urls-%s.txt' % page
        f = open(filename, 'w')
        # f.write(response.text)
        for articles in response.css("article.jsJustInArticle"):
            
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
        article = response.css("article.layout__item")

        url = response.url
        img = article.css("section.article-wrapper img::attr(src)").get()
        title = self.clean_string(article.css("div.programBlockHeader h1.article__title::text").get())
        date = self.clean_string(article.css("time::attr(datetime)").get())
        excerpt = article.css("section.article__body div.article-content__text > p::text").get()
        page = response.url.split("/")[2]
        insert_time = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        
        db = Database(url, img, title, excerpt, date, page, insert_time)
        
        for country in self.countries:
            db.fill_db(country)
        self.log('Saved data into DATABASE SUCCESS')
        
    def clean_string(self, mystring):
        return re.sub('[\t\r\n]+', '', mystring)