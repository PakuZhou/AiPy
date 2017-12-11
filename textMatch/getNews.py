# Function:
#       从厦门大学新闻网上爬取新闻标题，并存入数据库中。
# Time:
#       2017-11-28
# Author:
#       PakuZhou
# Environment：
#       Python 3.5.2


import requests
from lxml import html
import pymysql
import time
from bs4 import BeautifulSoup


def getNews(cursor, db, url):
    print('********开始爬取内容*******')
    res = requests.get(url)
    # 使用UTF-8编码
    res.encoding = 'UTF-8'
    # 使用剖析器为html.parser
    soup = BeautifulSoup(res.text, 'html.parser')
    # 定义三个列表分别用来存放每次请求得到的数据：url，标题，时间
    urls=[]
    titles=[]
    times=[]

    # 获取url和标题
    for news in soup.find_all('a'):
        tempURL=news.get('href')
        # 判断这个链接是不是标题的链接
        if 'page' in tempURL:
            urls.append(tempURL)
            titles.append(news.get('title'))

    # 获取时间
    for news in soup.find_all('div'):
        # 保证news.string不为空
        if news.string:
            # 判断news.string是否是时间戳
            if len(news.string)==10:
                # 判断是否为2017年的新闻
                if news.string[:4]=='2017':
                    times.append(news.string)

    # 这边要用times的长度来判断实际要存入的数量
    num=0
    while num!=len(times):
        try:
            sql ='''INSERT INTO top250(title, timestamp,url) 
                VALUES ("%s","%s","%s")'''%(titles[num],times[num],url[num])
        except Exception as e:
            print(url)

        try:
            # 执行sql语句
            cursor.execute(sql)
            # 提交到数据库执行
            db.commit()
            print(times[num]+'--commit')
        except Exception as e:
            # Rollback in case there is any error
            db.rollback()
            print (e)
        num=num+1



if __name__ == '__main__':
    # 打开数据库连接
    db = pymysql.connect(host="localhost", user="root", passwd="mysql", db="xmunews", charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    for i in range(1,10):
        start_url = 'http://news.xmu.edu.cn/1552/list'+str(i)+'.htm'
        getNews(cursor,db,start_url)
        # 暂停3s
        time.sleep(3)









