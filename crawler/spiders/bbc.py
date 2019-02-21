import scrapy
import json
import re
import mysql.connector
import datetime

class BBC(scrapy.Spider):
    name = "bbc"
    host = "localhost"
    user = "root"
    passwd = "google"
    database = "bembits"

    def start_requests(self):
        urls = [
            "https://www.bbc.com/",
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
        # f.write(response.text)
        for articles in response.css("li.media-list__item"):
            url = articles.css("div.media > a::attr(href)").get()
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
        article = response.css("div.column--primary")

        url = response.url
        img = article.css("figure span img::attr(src)").get()
        title = self.clean_string(article.css("h1.story-body__h1::text").get())
        date = self.clean_string(article.css("div.date::text").get())
        excerpt = article.css("p.story-body__introduction::text").get()
        page = response.url.split("/")[-4]
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