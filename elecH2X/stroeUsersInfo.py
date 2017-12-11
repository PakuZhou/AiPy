'''
代码说明：
    storeUsersInfo是elecH2X工程的代码，作为储存用户信息之用。
    这是更新的版本，更新之处在于
        （1）允许用户修改通知类型；（2）增加几个保留字段。

    代码分为3个步骤，由2个函数构成。
    步骤1：
    1-从xls文件中读取用户信息存入数据库中，类型为0（type=0）
        使用函数 【storeInfo（sheet，cur，conn，type）】
    2-从数据库中读取出所有用户的信息，并筛选出邮箱不重复的记录
        （保留最新的那条记录）。并将筛选之后的信息存入到selectUsers.xlsx。
        使用函数【selectUsers（cur）】
    3-从selectUsers.xlsx文件中读取用户信息存入数据库中，类型为1（type=1）
        使用函数 【storeInfo（sheet，cur，conn，type）】

    之所以采用如此复杂的做法是因为：直接在数据库中操！作！失！败！！！
    之所以大批量地读写数据库是因为:测试了下1500记录时整个操作耗时也就不到1秒，认为够用。
时间：
    2017-11-29
作者：
    怕酷周
'''

import re
import time
import xlrd
import pymysql
import xlwt


def storeInfo(sheet,cur,conn,type):
    if type==1:
        sql='''truncate users'''
        cur.execute(sql)
        print('\n×××××××××××××××数据库中的表已清空×××××××××××××××\n')

    print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n开始从表格中读取数据到数据库中\n')

    # 创建插入SQL语句
    query = 'insert into users(join_time,xq,lou,room,freq,state,new,ad_type,addr,stunum) values (%s, %s,%s, %s, %s,%s,%s,%s,%s,%s)'
    today=time.strftime("%Y-%m-%d", time.localtime())

    if type == 0:
        # 创建一个for循环迭代读取xls文件每行数据的, 从第二行开始是要跳过标题行
        for r in range(1, sheet.nrows):
              #从xls中读取 校区代码
              xqtemp=re.findall('\d+',sheet.cell(r,6).value)
              xq=xqtemp[0]
              #从xls中读取 宿舍楼名 以及 房间号
              lou= sheet.cell(r,7).value
              room = sheet.cell(r,8).value
              #从xls中读取 邮箱地址 以及 通知频率
              addr = sheet.cell(r,9).value
              freq = sheet.cell(r,10).value
              #从xls中读取 学号
              sntemp=re.findall('\d+',sheet.cell(r,11).value+"999")
              stunum = sntemp[0]

              #用户状态，1代表提供服务，0代表拒绝服务
              state = "1"
              #是否为信用户，1代表是，0代表不是
              new = "1"
              #接受广告类型，此字段暂保留
              ad_type="0"

              values = (
                  str(today),
                  str(xq),
                  str(lou),
                  str(room),
                  str(freq),
                  str(state),
                  str(new),
                  str(ad_type),
                  str(addr),
                  str(stunum)
              )
              print(values[1:4])
              # 执行sql语句
              cur.execute(query, values)
              #end for
    elif type ==1:
        # 创建一个for循环迭代读取xls文件每行数据的, 从第二行开始是要跳过标题行
        for r in range(1, sheet.nrows):
              #从xlsx中读取 校区代码
              xq = sheet.cell(r,2).value
              #从xlsx中读取 宿舍楼名 以及 房间号
              lou= sheet.cell(r,3).value
              room = sheet.cell(r,4).value
              #从xlsx中读取 邮箱地址 以及 通知频率
              addr = sheet.cell(r,9).value
              freq = sheet.cell(r,5).value
              #从xlsx中读取 学号
              stunum = sheet.cell(r,10).value
              #用户状态，1代表提供服务，0代表拒绝服务
              state = "1"
              #是否为信用户，1代表是，0代表不是
              new = "1"
              #接受广告类型，此字段暂保留
              ad_type="0"

              values = (
                  str(today),
                  str(xq),
                  str(lou),
                  str(room),
                  str(freq),
                  str(state),
                  str(new),
                  str(ad_type),
                  str(addr),
                  str(stunum)
              )
              print(values[1:4])
              # 执行sql语句
              cur.execute(query, values)
              #end for

    conn.commit()
    columns = str(sheet.ncols)
    rows = str(sheet.nrows)
    print ("\n成功导入 " +str(int(columns)-1) + " 列 " + str(int(rows)-1) + " 行数据到MySQL数据库!\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")



def selectUsers(cur):

    sql=''' SELECT * FROM users '''
    count = cur.execute(sql)
    print ('\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n数据库中一共有 %s 条记录。' % count)
    if count == 0:
        return

    #重置游标位置
    cursor.scroll(0,mode='absolute')
    #搜取所有结果
    results = cursor.fetchall()

    #获取MYSQL里的数据字段
    fields = cur.description
    #将字段写入到EXCEL新表的第一行
    wbk = xlwt.Workbook()
    sheet = wbk.add_sheet('users',cell_overwrite_ok=True)
    for ifs in range(0,len(fields)):
        sheet.write(0,ifs,fields[ifs][0])

    #对数据库中的数据进行筛选，并保存
    ics =0
    addrs = []
    for row in range(1,len(results)+1)[::-1]:

        addr = results[row-1][9]
        if addr in addrs:
            continue
        else:
            addrs.append(addr)
            ics+=1
            for jcs in range(0,len(fields)):
                sheet.write(ics,jcs,results[row-1][jcs])
    wbk.save('./selectUsers.xlsx')
    print('从数据库中筛选出%d条不重复记录,已成功导出。'%(len(addrs)-1))
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')



if __name__ == '__main__':

    # 打开数据库连接
    db = pymysql.connect(host="localhost", user="root",passwd="mysql", db="h2x", charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    #步骤1
    book = xlrd.open_workbook("./10_7_0.xls")
    sheet = book.sheet_by_name("Sheet1")

    #步骤2
    storeInfo(sheet,cursor,db,0)

    selectUsers(cursor)

    #步骤3
    book = xlrd.open_workbook("./selectUsers.xlsx")
    sheet = book.sheet_by_name("users")
    storeInfo(sheet,cursor,db,1)

    # 关闭连接
    if cursor:
        cursor.close()
    if db:
        db.close()
