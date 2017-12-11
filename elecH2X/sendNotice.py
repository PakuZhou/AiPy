'''
Function:
    1）从用户信息表中读取用户信息；
    2）根据用户信息查询电费信息；
    3）将电费信息发送给用户。
Author：
    PakuZhou
Time：
    2017-11-09
'''
import datetime
import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import pymysql
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

# 发送电费信息给用户
def sendMail(location,addr,data,logFile):

    #收发配置
    sender = '******************@stu.xmu.edu.cn'
    receiver = addr
    smtpserver = 'smtp.stu.xmu.edu.cn'
    username = '******************@stu.xmu.edu.cn'
    password = '******************'
    #邮件信息
    subject = '[%s-%s-%s] %.2f元，%.2f度。'%(location[0],location[1],location[2],data[0],data[1])
    notice="<p>%s同学，你好：</p>"%addr
    notice=notice+"<p>你查询的宿舍电费信息为：</p>"
    url2="******************" #电费查询地址
    url1="******************" #电费充值地址
    url3="******************"#代码展示地址
    url4="******************"#问卷地址
    notice=notice+'''
            <p>【%s-%s-%s】电费余额:</p>
            '''%(location[0],location[1],location[2])
    notice=notice+"<p>%.2f 元 ；%.2f 度。</p>"%(data[0],data[1])
    notice=notice+"<p>==========</p>"
    notice=notice+'''
                    <p><a href="%s">【在线交电费】厦门大学校园卡电子服务平台</a></p>
                    <p><a href="%s">【电费查询】厦门大学学生宿舍智能控电电费查询</a></p>
                    <p><a href="%s">【程序源代码】</a></p>
                    <p><a href="%s">【更改通知】填写问卷即可订阅/取消电费通知或者修改通知类型</a></p>
                    <p>任何意见/建议/反馈/问题，直接回复:)</p>
                    '''%(url1,url2,url3,url4)
    msg = MIMEText(notice,'html','utf-8')#中文需参数‘utf-8'，单字节字符不需要
    msg['Subject'] = Header(subject, 'utf-8')

    #发送邮件
    try:
        smtp = smtplib.SMTP()
        smtp.connect('smtp.stu.xmu.edu.cn')
        smtp.login(username, password)
        smtp.sendmail(sender, receiver, msg.as_string())
        logFile.write ("SUC:[%s-%s-%s]\n"%(location[0],location[1],location[2]))
    except smtplib.SMTPException as e:
        logFile.write ("ERR:[%s-%s-%s]: %s\n"%(location[0],location[1],location[2],str(e)))
    smtp.quit()


# 获取某一个宿舍的剩余电费及金额
def getLeft(location,driver,logFile):
    leftData=[0.0,0.0]

    driver.get('******************')
    #下拉选择校区
    sl_xq = Select(driver.find_element_by_id('drxiaoqu'))
    op_xq=sl_xq.select_by_value(location[0])
    #下拉选择宿舍楼
    sl_l=Select(driver.find_element_by_id('drlou'))
    op_l=sl_l.select_by_value(location[1])
    #文本框填写房间号
    elem=driver.find_element_by_id('txtRoomid')
    elem.clear()
    elem.send_keys(location[2])
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
            logFile.write("SUC:"+str(location)+"剩余:"+str(fmoney)+"元；"+str(felec)+"度\n")


    leftData[0]=fmoney
    leftData[1]=felec
    return leftData


# 根据服务类型从数据库中提取用户信息
def queryU2E(cursor,serviceType):
    sql="SELECT * FROM users WHERE freq = %d"%serviceType
    cursor.execute(sql)
    results = cursor.fetchall()
    return results
    print("queryU2E---end")

# 从数据库中提取新用户信息
def queryNew(cursor,isNew):
    sql="SELECT * FROM users WHERE new = %d"%isNew
    cursor.execute(sql)
    results = cursor.fetchall()
    return results
    print("queryNew---end")

# 更新新用户信息
def updateNew(cursor,db):
    print('\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n开始更新数据库\n')
    sql = '''UPDATE users SET new=0 '''
    result = cursor.execute(sql)
    db.commit()
    db.close()
    print('【 %s 条】记录正在被更新......\n'%(str(result)))
    print("成功更新数据库\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

# 给新用户发送确认邮件
def sendConf(location,addr,data,type,logFile):
    #收发配置
    sender = '******************@stu.xmu.edu.cn'
    receiver = addr
    smtpserver = 'smtp.stu.xmu.edu.cn'
    username = '******************@stu.xmu.edu.cn'
    password = '******************'

    

    #邮件信息
    subject = '[确认邮件] %s-%s-%s'%(location[0],location[1],location[2])
    url2="******************" #电费查询地址
    url1="******************" #电费充值地址
    url3="******************「电费查询信息代码」"#代码展示地址
    url4="******************"#问卷地址

    notice="<p> %s 同学，你好：</p>"%addr
    notice=notice+"<p>你已成功订阅电费信息通知。</p>"
    notice=notice+"<p>这是确认邮件，你的信息如下：</p>"
    notice=notice+"<p>【宿舍】： %s-%s-%s"%(location[0],location[1],location[2])
    notice=notice+"<p>【类型】： %s </p>"%type
    notice=notice+"<p>【注释】： </p>"
    notice=notice+"<p> ------（类型0）每天通知;</p>"
    notice=notice+"<p> ------（类型1）每周六通知；</p>"
    notice=notice+"<p> ------（类型2）电费低于10度每天通知； </p>"
    notice=notice+"<p> ------（类型4）取消通知。</p>"
    notice=notice+'''<p><a href="%s">若以上信息有误，点此处重新填写问卷即可。</a></p>'''%url4
    notice=notice+"<p>你所在宿舍的电费信息：</p>"
    notice=notice+'''
            <p>【%s-%s-%s】电费余额 %.2f 元 ；%.2f 度。</p>
            '''%(location[0],location[1],location[2],data[0],data[1])
    notice=notice+"<p>==========</p>"

    notice=notice+'''
                    <p><a href="%s">【在线交电费】厦门大学校园卡电子服务平台</a></p>
                    <p><a href="%s">【电费查询】厦门大学学生宿舍智能控电电费查询</a></p>
                    <p><a href="%s">【程序源代码】</a></p>
                    <p><a href="%s">【更改通知】填写问卷即可订阅/取消电费通知或者修改通知类型</a></p>
                    <p>任何意见/建议/反馈/问题，直接回复:)</p>
                    '''%(url1,url2,url3,url4)
    msg = MIMEText(notice,'html','utf-8')#中文需参数‘utf-8'，单字节字符不需要
    msg['Subject'] = Header(subject, 'utf-8')

    #发送邮件
    try:
        smtp = smtplib.SMTP()
        smtp.connect('smtp.stu.xmu.edu.cn')
        smtp.login(username, password)
        smtp.sendmail(sender, receiver, msg.as_string())
        logFile.write ("<new user>SUC:[%s-%s-%s]\n"%(location[0],location[1],location[2]))
    except smtplib.SMTPException as e:
        logFile.write ("<new user>ERR:[%s-%s-%s]: %s\n"%(location[0],location[1],location[2],str(e)))
    smtp.quit()


if __name__ == '__main__':
    # 打开数据库连接
    db = pymysql.connect(host="localhost", user="root", passwd="******************", db="h******************x", charset='utf8')
    # 使用cursor()方法获取操作游标
    cursor = db.cursor()
    #开webdriver
    driver = webdriver.Chrome()

    queryErr = 0
    num=0
    mailLog=open('./mailLog','w')
    mailLog.truncate()
    mailLog=open('./mailLog','a')
    querryLog = open('./querryLog','w')
    querryLog.truncate()
    querryLog=open('./querryLog','a')



    location = ["","",""]
    addr = ""
    data = [0.0,0.0]


    # 根据订阅类型给用户发送信息
    for type in range(0,3):
        querryLog.write("==============================================\nfreq = %d\n"%type)
        if datetime.date.today().weekday() != 6 and type==1:
            continue
        userNew=queryU2E(cursor,type)
        for user in userNew:
            location[0]=user[2]
            location[1]=user[3]
            location[2]=user[4]
            addr=user[9]
            freq=user[5]
            try:
                data=getLeft(location,driver,querryLog)
                queryErr = 0
            except:
                queryErr = 1
                querryLog.write('ERR:%s !!!!!!!!!!!!!!!!!!!!!!!!!!\n'%str(location))
                # 查询出现错误后关掉浏览器重新打开并继续循环查询过程
                time.sleep(10)
                driver.quit()
                driver = webdriver.Chrome()
                continue
            #查询没有出现错误，发送邮件
            if queryErr ==0:
                #print("%s ,%s, %s"%(str(location),str(addr),str(data)))
                if data[1] > 10 and type==2:
                    continue
                sendMail(location,addr,data,mailLog)
                if num == 0:
                    time.sleep(10)
                else:
                    num+=1
                    time.sleep(2)


    # 给新用户发送确认邮件
    #！这段代码块必须被放在最后！
    #因为执行updateNew之后会关闭数据库连接
    querryLog.write("==============================================\nnew users\n")
    userNew=queryNew(cursor,1)
    for user in userNew:
        location[0]=user[2]
        location[1]=user[3]
        location[2]=user[4]
        addr=user[9]
        freq=user[5]
        try:
            data=getLeft(location,driver,querryLog)
            queryErr = 0
        except:
            queryErr = 1
            querryLog.write('<new user>ERR:%s !!!!!!!!!!!!!!!!!!!!!!!!!!\n'%str(location))
            # 查询出现错误后关掉浏览器重新打开并继续循环查询过程
            driver.quit()
            driver = webdriver.Chrome()
            continue
        #查询没有出现错误，发送邮件
        if queryErr ==0:
            sendConf(location,addr,data,freq,mailLog)
            time.sleep(2)
    driver.quit()
    updateNew(cursor,db)


