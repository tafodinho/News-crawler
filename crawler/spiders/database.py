import json
import re
import mysql.connector
import datetime


class Database:
    host = 'localhost'
    user = 'root'
    passwd = 'google'
    database = 'bembits'
    
    def __init__(self, url, image, title, excerpt, date, page, insert_time):
        self.url = url
        self.image = image
        self.title = title
        self.excerpt = excerpt
        self.date = date
        self.page = page
        self.insert_time = insert_time

        self.mydb = self.mysql_connect()

    
    def mysql_connect(self):
        return mysql.connector.connect(
            host = self.host, 
            user = self.user, 
            passwd = self.passwd, 
            database = self.database
        )

    def fill_db(self, table):
        country = table[:-1]
        
        db_cursor = self.mydb.cursor()
        sql1 = "SELECT * FROM " + table + " WHERE title = '%s'" % self.title
        db_cursor.execute(sql1)
        result = db_cursor.fetchall()
        if len(result) > 0:
            return
        sql = "INSERT INTO " + table + " (name, image, title, excerpt, date, site, url, created_at, updated_at) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (country, self.image, self.title, self.excerpt, self.date, self.page, self.url, self.insert_time, self.insert_time)
        
        db_cursor.execute(sql, val)
        self.commit_to_db()
        
    def commit_to_db(self):
        self.mydb.commit()
