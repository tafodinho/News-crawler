import scrapy
import json
import re
import mysql.connector
import datetime


class Aljazeera(scrapy.Spider):
    name = "aljazeera"

    host = 'localhost'
    user = 'root'
    passwd = 'google'
    database = 'bembits'

    def start_requests(self):
        urls = [
            'https://www.aljazeera.com/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def mysql_connect(self):
        return mysql.connector.connect(
            host = self.host, 
            user = self.user, 
            passwd = self.passwd, 
            database = self.database
        )

    def parse(self, response):
        links_crawled = []
        page = response.url.split("/")[-2]
        filename = 'urls-%s.txt' % page
        f = open(filename, 'w')

        for articles in response.css("div.latest-news-topic"):
            url = response.url[:-1] + articles.css("a::attr(href)").get()
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
        print(response)
        url = response.url
        img = "https://www.aljazeera.com" + article.css("figure.main-article-mediaCaption > div.main-article-media > img::attr(src)").get()
        title = self.clean_string(article.css("div.article-heading h1::text").get())
        date = self.clean_string(article.css("time::text").get())
        excerpt = article.css("p.article-heading-des::text").get()
        page = response.url.split("/")[2]
        insert_time = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        
        mydb = self.mysql_connect()
        db_cursor = mydb.cursor()
        sql1 = "SELECT * FROM cameroons WHERE title = '%s'" % title
        db_cursor.execute(sql1)
        result = db_cursor.fetchall()
        if len(result) > 0:
            return
        sql = "INSERT INTO cameroons (name, image, title, excerpt, date, site, url, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = ('cameroon', img, title, excerpt, insert_time, page, url, insert_time, insert_time)

        db_cursor.execute(sql, val)
        mydb.commit()
        self.log('Saved data into DATABASE SUCCESS')
        
    def clean_string(self, mystring):
        return re.sub('[\t\r\n]+', '', mystring)
       