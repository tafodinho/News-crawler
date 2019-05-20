import scrapy
import json
import re
import mysql.connector
import datetime
from .database import Database

class TheNYTimes(scrapy.Spider):
    name = "thenytimes"
    table = "americas"

    def start_requests(self):
        urls = [
            'https://www.nytimes.com/section/us',
        ]
        for url in urls:
            yield scrapy.Request(url=url, meta = {
                      'dont_redirect': True,
                      'handle_httpstatus_list': [302]
                  },callback=self.parse)

    def parse(self, response):
        links_crawled = []
        page = response.url.split("/")[-2]
        filename = 'urls-%s.txt' % page
        f = open(filename, 'w')

        for articles in response.css("li.css-ye6x8s"):
            url = articles.css("div.css-1cp3ece a::attr(href)").get()
            # print("\n\n\n\n\n\n\n\n"+url+"\n\n\n\n\n\n\n\n\n\\")
            if url[0] is '/':
                url = response.url[:-11] + url
            if url in links_crawled:
                continue
            try:
                f.write(json.dumps({'url': url}))
                f.write('\n')
                links_crawled.append(url)
                request = scrapy.Request(url=url, callback=self.parse1)
                request.meta['dont_redirect'] = True
                yield request
            except:
                pass
        
        self.log('Saved file %s' % filename)
        f.close()

    def parse1(self, response):
        article = response.css("header.css-1n5gntz")
        url = response.url
        print(dir(response))
        f = open("testing.txt", 'wb')
        f.write(response.body)
        f.close()
        img = article.css("figure img::attr(src)").get()
        title = self.clean_string(article.css("div.css-1vkm6nb::text").get())
        print("\n\n\n\n\n\n\n\n"+title+"\n\n\n\n\n\n\n\n\n\\")
        date = self.clean_string(article.css("header time::attr(datetime)").get())
        excerpt = article.css("header figcaption span.css-8i9d0s::text").get()
        page = response.url.split("/")[2]
        insert_time = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
        
        db = Database(url, img, title, excerpt, date, page, insert_time)
        db.fill_db(self.table)

        self.log('Saved data into DATABASE SUCCESS')
        
    def clean_string(self, mystring):
        return re.sub('[\t\r\n]+', '', mystring)
       