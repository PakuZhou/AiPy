# This is a script that writes data from MySQL to csv

import csv
import pymysql


def main():
    # 连接数据库
    conn = pymysql.connect(host="localhost", user="root", passwd="mysql", db="xmunews", charset='utf8')
    cur = conn.cursor()

    # 以写的方式打开 csv 文件并将内容写入到w
    f = open("./titles.csv", 'w')
    write_file = csv.writer(f)

    # 从 student 表里面读出数据，写入到 csv 文件里
    cur.execute("select * from top250")
    while True:
        row = cur.fetchone()    #获取下一个查询结果集为一个对象
        if not row:
            break
        write_file.writerow(row)    #csv模块方法一行一行写入
    f.close()

    # 关闭连接
    if cur:
        cur.close()
    if conn:
        conn.close()


if __name__ == '__main__':
    main()
