'''
Function:
    获取某一个宿舍的剩余电费信息，并将得到的数据存入数据库。
    本程序爬取的是翔安校区映雪楼区，映雪楼1～映雪6的所有宿舍。
Author：
    PakuZhou
Time：
    2017-11-08

=====================================================
Version 2.0
【增加】查询中断之后重连功能。
        防止由于网络等异常原因导致查询中断使得程序异常退出，查询数据不完整。
【优化】查询过程。
        将原来的每个宿舍查询都要打开一次浏览器改为查询一栋楼才打开一次浏览器，
        整个过程耗时由原来的90分钟缩短只15分钟！

代码说明：

Time：
    2017-11-30
Author：
    PakuZhou

'''

import re
import datetime
import pymysql
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select



def storeInfo2(xqCode,louList,roomList,elecList):
    print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n开始存储数据')
    fmoney=999.99
    numRoom = 0
    date = datetime.date.today()

    for lou in louList:
        for room in roomList:

            sql ='''INSERT INTO elec_info(xq,lou,room,balance,elec,time) 
                VALUES ("%s","%s","%s","%f","%f","%s")'''\
                 %(xqCode,lou,room, fmoney,elecList[numRoom],date)

            try:
                # 执行sql语句
                cursor.execute(sql)
                # 提交到数据库执行
                db.commit()
                print('【 %s %s %s： %.2f 】commited！'%(xqCode,lou,room,elecList[numRoom]))
                numRoom = numRoom+1
            except Exception as e:
                # Rollback in case there is any error
                db.rollback()
                print (e)
    print('\n共有 %d 间宿舍信息被存储。\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n'%numRoom)

def getLeft2(xqCode,louList,roomList):
    print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n 开始爬取 【 %s 校区 】 的电费信息'%xqCode)
    leftElec = []

    driver = webdriver.Chrome()
    driver.get('http://elec.xmu.edu.cn/PdmlWebSetup/Pages/SMSMain.aspx')

    for lou in louList:
        for room in roomList:
            try:
                #下拉选择校区
                sl_xq = Select(driver.find_element_by_id('drxiaoqu'))
                op_xq=sl_xq.select_by_value(xqCode)
                #下拉选择宿舍楼
                sl_l=Select(driver.find_element_by_id('drlou'))
                op_l=sl_l.select_by_value(lou)
                #文本框填写房间号
                elem=driver.find_element_by_id('txtRoomid')
                elem.clear()
                elem.send_keys(room)
                elem.send_keys(Keys.RETURN)

                #解析返回的网页获取数据
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                for label in soup.find_all('label'):
                    labelstring=str(label)
                    if 'lableft' in labelstring:
                        #将数字提取出来
                        left=re.findall('\d+',labelstring)
                        #再将数字拼成实际的浮点数
                        fmoney=float(left[0]+"."+left[1])
                        felec=float(left[2]+"."+left[3])
                        leftElec.append(felec)
                        #print(felec)

            except:
                print('【%s,%s,%s】查询时出现错误！\n1分钟之后重新连接'%(xqCode,lou,room))
                felec=999.99
                leftElec.append(felec)
                time.sleep(60)
                continue

    driver.quit()
    print('\n查询过程结束。\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
    return leftElec


if __name__ == '__main__':


    # 打开数据库连接
    db = pymysql.connect(host="localhost", user="root",passwd="mysql", db="h2x", charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()

    #设置要查询的宿舍列表
    xqList=["01","02","03","04","05","06","07","08","09",
            "10","11","12",
            "21","22","23","24","25","26","27","28","29",
            "30","31","32","33","34","35",
            "40","41","42",
            "50","51","52"]
    louList52=["映雪1","映雪2","映雪3","映雪4","映雪5","映雪6"]
    roomList=[]
    for i in range (2,12):
        room=""
        if i<10 :
            room=room+"0"+str(i)
        else:
            room=room+str(i)
        for j in range(1,15):
            roomtemp=room
            if j<10:
                roomq=roomtemp+"0"+str(j)
            else:
                roomq=roomtemp+str(j)
            roomList.append(roomq)

    leftElec = []
    #查询
    leftElec = getLeft2(xqList[-1],louList52,roomList)
    print(leftElec)
    #存储
    storeInfo2(xqList[-1],louList52,roomList,leftElec)
