
import datetime
import time
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import pymysql
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

class runLog(object):
    def __init__(self,logPath='/home/pakuzhou/PycharmProjects/elecH2X/test/runLog.txt'):
        self.file = open(logPath,'a')
        self.addTime()

    def addTime(self):
        today = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.file.write("\n[{}]++++++++++++++++++++++++++++++++++++\n".format(today))

    def writeLine(self,description="Hello World！"):
        self.file.write("({})====================================\n".format(description))

    def writeLog(self,something):
        self.file.write("\t {} \n".format(something))

class getElecInfo(object):

    def __init__(self,
                 runLog,
                 website="http://elec.xmu.edu.cn/PdmlWebSetup/Pages/SMSMain.aspx",
                 driver = webdriver.Chrome()):
        self.site = website
        self.driver = driver
        self.runLog = runLog

    def _getDataFromPage(self,page_source):
        soup = BeautifulSoup(page_source, 'html.parser')
        for label in soup.find_all('label'):
            labelstring=str(label)
            if 'lableft' in labelstring:
                #将数字提取出来
                left=re.findall('\d+',labelstring)
                #再将数字拼成实际的浮点数
                fmoney = float(left[0]+"."+left[1])
                felec = float(left[2]+"."+left[3])

        return fmoney,felec

    def getLeftInfo(self,location):
        try:
            self.driver.get(self.site)
            #下拉选择校区
            sl_xq = Select(self.driver.find_element_by_id('drxiaoqu'))
            op_xq=sl_xq.select_by_value(location['xq'])
            #下拉选择宿舍楼
            sl_l=Select(self.driver.find_element_by_id('drlou'))
            op_l=sl_l.select_by_value(location['lou'])
            #文本框填写房间号
            elem=self.driver.find_element_by_id('txtRoomid')
            elem.clear()
            elem.send_keys(location['room'])
            elem.send_keys(Keys.RETURN)
        except:
            self.runLog.writeLog("ERR:{}!!!!!!!!!!!!!!!!!!!!!!!!!!!!".format(location))
            return False,None,None

        leftMoney,leftElec = self._getDataFromPage(self.driver.page_source)
        self.runLog.writeLog("SUC:{},left_money:{},left_elec:{}.\n".format(location,leftMoney,leftElec))
        return  True,leftMoney,leftElec

    def closeBrowser(self):
        self.driver.quit()

class mailSender(object):
    def __init__(self,
                 runLog,
                 sender='****************@stu.xmu.edu.cn',
                 smtpserver = 'smtp.stu.xmu.edu.cn',
                 username = '*************@stu.xmu.edu.cn',
                 password = '*************'
                 ):
        self.sender = sender
        self.smtpserver = smtpserver
        self.username = username
        self.password = password
        self.smtp = smtplib.SMTP()
        self.runLog = runLog
        self.loginSmtpServer()

    def loginSmtpServer(self):
        try:
            self.smtp.connect(self.smtpserver)
            self.smtp.login(self.username,self.password)
            self.runLog.writeLog("Login SUC.")
        except smtplib.SMTPException as e:
            self.runLog.writeLog("Login ERR!{}".format(e))

    def sendMail(self,msg="Hello World!",toAddr='3045531598@qq.com'):
        try:
            self.smtp.sendmail(self.sender, toAddr, msg.as_string())
            self.runLog.writeLog("SUC {} ".format(toAddr))
        except:
            self.runLog.writeLog("ERR {}".format(toAddr))
            return

    def quitSMTP(self):
        self.smtp.quit()

class mailMsg(object):

    def __init__(self):
        self.msg = MIMEMultipart()
        self.urlElecQuerry = "http://elec.xmu.edu.cn/PdmlWebSetup/Pages/SMSMain.aspx" #电费查询地址
        self.urlElecCharge = "http://ecardservice.xmu.edu.cn/" #电费充值地址
        self.urlCodeShow = "https://shimo.im/doc/wYcxGoVhdM0TwgtE?r=XPRDMG/「电费查询信息代码」"#代码展示地址
        self.urlSharing = "https://www.wjx.top/jq/17948119.aspx"#问卷地址

    def makeMsg(self):
        return self.msg

class imgMsg(mailMsg):

    imgPath = '/home/pakuzhou/PycharmProjects/elecH2X/test/new_year.png'
    imgName = 'elecH2X.png'

    def makeMsg(self,
                userName,
                money,
                elec,
                location):
        #邮件内容
        subject = '[T%s-%s-%s] %.2f元，%.2f度。'%(location['xq'],location['lou'],location['room'],money,elec)
        notice = "<p>%s同学，你好：</p>"%userName + \
                 "<p>你查询的宿舍电费信息为：</p>"+\
                 '''
                  <p>【%s-%s-%s】电费余额:</p>
                 '''%(location['xq'],location['lou'],location['room'])
        notice += "<p>%.2f 元 ；%.2f 度。</p>"%(money,elec)+\
                  '<p><img src="cid:0"></p>'+'''
                        <p><a href="%s">【在线交电费】厦门大学校园卡电子服务平台</a></p>
                        <p><a href="%s">【电费查询】厦门大学学生宿舍智能控电电费查询</a></p>
                        <p><a href="%s">【程序源代码】</a></p>
                        <p><a href="%s">【更改通知】填写问卷即可订阅/取消电费通知或者修改通知类型</a></p>
                        <p>任何意见/建议/反馈/问题，直接回复:)</p>
                        '''%(self.urlElecCharge,self.urlElecQuerry,self.urlSharing,self.urlCodeShow)

        self.msg.attach(MIMEText(notice, 'html', 'utf-8'))
        self.msg['Subject'] = Header(subject, 'utf-8')

        # 添加附件就是加上一个MIMEBase，从本地读取一个图片:
        with open(self.imgPath, 'rb') as f:
            # 设置附件的MIME和文件名，这里是png类型:
            mime = MIMEBase('image', 'png', filename=self.imgName)
            # 加上必要的头信息:
            mime.add_header('Content-Disposition', 'attachment', filename=self.imgName)
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            # 把附件的内容读进来:
            mime.set_payload(f.read())
            # 用Base64编码:
            encoders.encode_base64(mime)
            # 添加到MIMEMultipart:
            self.msg.attach(mime)

        return self.msg

class confMsg(mailMsg):

    def makeMsg(self,userName,freq,location):

        subject = '[T确认邮件] %s-%s-%s'%(location['xq'],location['lou'],location['room'])
        notice = "<p> %s 同学，你好：</p>"%userName +\
                 "<p>你已成功订阅电费信息通知。</p>" +\
                 "<p>这是确认邮件，你的信息如下：</p>" +\
                 "<p>【宿舍】： %s-%s-%s"%(location['xq'],location['lou'],location['room'])

        if freq == 0:
            freqNotice = "每天通知"
        elif freq == 1:
            freqNotice = "每周六通知"
        elif freq == 2:
            freqNotice = "电费低于10度每天通知"
        elif freq == 4:
            freqNotice = "取消通知"

        notice += "<p>【类型】： %s </p>"%freqNotice

        notice += '''<p><a href="%s">若以上信息有误，点此处重新填写问卷即可。</a></p>'''%self.urlSharing

        self.msg.attach(MIMEText(notice, 'html', 'utf-8'))
        self.msg['Subject'] = Header(subject, 'utf-8')

        return self.msg

class broadMsg(mailMsg):
    imgPath = '/home/pakuzhou/PycharmProjects/elecH2X/test/new_year.png'
    imgName = 'elecH2X.png'

    def makeMsg(self,userName):
        subject = '[新年好！] '
        notice = "<p> %s 同学，你好：</p>"%userName +\
                 "<p>这是一条广播信息。</p>" +\
                '<p><img src="cid:0"></p>'
        self.msg.attach(MIMEText(notice, 'html', 'utf-8'))
        self.msg['Subject'] = Header(subject, 'utf-8')

        # 添加附件就是加上一个MIMEBase，从本地读取一个图片:
        with open(self.imgPath, 'rb') as f:
            # 设置附件的MIME和文件名，这里是png类型:
            mime = MIMEBase('image', 'png', filename=self.imgName)
            # 加上必要的头信息:
            mime.add_header('Content-Disposition', 'attachment', filename=self.imgName)
            mime.add_header('Content-ID', '<0>')
            mime.add_header('X-Attachment-Id', '0')
            # 把附件的内容读进来:
            mime.set_payload(f.read())
            # 用Base64编码:
            encoders.encode_base64(mime)
            # 添加到MIMEMultipart:
            self.msg.attach(mime)

        return self.msg

class dbOperator(object):
    def __init__(self,host="localhost", user="root", passwd="mysql", db="h2x", charset='utf8'):
        self.db = pymysql.connect(host=host, user=user, passwd=passwd, db=db, charset=charset)
        self.cursor = self.db.cursor()

    def selectUsers(self,freq):
        sql="SELECT * FROM users WHERE freq = %d"%freq
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results

    def selectNewers(self,isNew):
        sql="SELECT * FROM users WHERE new = %d"%isNew
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results

    def selectAlivers(self,mark=4):
        sql="SELECT * FROM users WHERE new != %d"%mark
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results

    def updateNewers(self):
        print('\n^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n开始更新数据库\n')
        sql = '''UPDATE users SET new=0 '''
        result = self.cursor.execute(sql)
        self.db.commit()
        print('【 %s 条】记录正在被更新......\n'%(str(result)))
        print("成功更新数据库\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")

    def dbClose(self):
        self.db.close()

if __name__ == '__main__':

    location = {'xq':'52','lou':'映雪19','room':'0205'}

    userName = '2315787681@qq.com'
    money = 20.0
    elec = 80.0
    freq = 2

    rl = runLog()
    ms = mailSender(rl)
    gei = getElecInfo(rl)
    dbo = dbOperator()
    im = imgMsg()
    cm = confMsg()
    bm = broadMsg()

    # for i in range(3):
    #     rl.writeLine("freq = {}".format(i))
    #     if datetime.date.today().weekday() != 6 and type==1:
    #         continue
    #     users = dbo.selectUsers(i)
    #     for user in users:
    #         location['xq']=user[2]
    #         location['lou']=user[3]
    #         location['room']=user[4]
    #         addr=user[9]
    #         freq=user[5]
    #
    #         querySUC,money,elec = gei.getLeftInfo(location=location)
    #         #查询没有出现错误，发送邮件
    #         if querySUC:
    #             if elec > 10 and type==2:
    #                 continue
    #             imsg = im.makeMsg(addr,money,elec,location)
    #             ms.sendMail(imsg,addr)

    # bmsg = bm.makeMsg(userName)
    # ms.sendMail(bmsg,userName)

    rl.writeLine("Broadcast")
    users = dbo.selectAlivers()
    for user in users:
        location['xq']=user[2]
        location['lou']=user[3]
        location['room']=user[4]
        addr=user[9]
        freq=user[5]
        bmsg = bm.makeMsg(addr)
        ms.sendMail(bmsg,toAddr=addr)
        time.sleep(5)

    dbo.dbClose()
    ms.quitSMTP()
    gei.closeBrowser()
