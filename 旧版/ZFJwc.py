from lxml import etree
import warnings
import requests
import importlib
from bs4 import BeautifulSoup
import sys
import recognizer
from getpass import getpass

def getInfor(response, xpath):
    content = response.content.decode('gb2312')  # 网页源码是gb2312要先解码
    selector = etree.HTML(content)
    try:
        infor = selector.xpath(xpath)[0]
    except IndexError as e:
        return []
    return infor

class Student:
    def __init__(self , number , password):
        self.name = ''
        self.number = number
        self.password = password

class CsuftJwc:
    def __init__(self, student,ip):
        importlib.reload(sys)
        #初始参数
        self.ip = ip
        self.yes = True
        self.urlhead = "http://"+self.ip
        self.login = self.urlhead + '/default2.aspx'
        self.checkInfo = self.urlhead + '/xsgrxx.aspx?xh={username}&xm={name}&gnmkdm=N121501'
        self.checkNo = self.urlhead + '/xs_main.aspx?xh={username}'
        self.checkTimetable = self.urlhead + '/xskbcx.aspx?xh={username}&xm={name}&gnmkdm=N121603'
        self.checkScore = self.urlhead + '/xscjcx.aspx?xh={username}&xm={name}&gnmkdm=N121618'
        self.checkLevel = self.urlhead+'/xsdjkscx.aspx?xh={username}&xm={name}&gnmkdm=N121606'
        self.student = student
        self.session = requests.session()
        self.session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
        }

    def checkcode(self):
        #获取验证码并下载到本地
        imgUrl = self.urlhead+"/CheckCode.aspx?"
        imgresponse = self.session.get(imgUrl, stream=True)
        pic = imgresponse.content
        with open('1.png', 'wb') as f:
            f.write(pic)

    def Yes(self):
        return self.yes

    def getName(self, response):
        #获取学生基本信息
        text = getInfor(response,'//*[@id="xhxm"]/text()')
        if text:
            text = text.replace(" ","")
            self.student.name = str(text.replace("同学","").encode("gb2312"))
            print("欢迎"+text+"!")
        else:
            self.yes = False
            print("密码错误！")

    def Login(self):
        #访问教务系统
        response = self.session.get(self.login)
        # 使用xpath获取__VIEWSTATE
        selector = etree.HTML(response.content)
        __VIEWSTATE = selector.xpath('//*[@id="form1"]/input/@value')[0]
        self.checkcode()
        #手动输入验证码
        #code = raw_input("输入验证码：")
        code = recognizer.recognize_checkcode('1.png')
        #构建post数据
        RadioButtonList1 = '学生'.encode('gb2312')
        data = {
            '__VIEWSTATE': __VIEWSTATE,
            'txtUserName': self.student.number,
            'TextBox2': self.student.password,
            'txtSecretCode': code,
            'RadioButtonList1': RadioButtonList1,
            'Button1': '',
            'lbLanguage': '',
            'hidPdrs': '',
            'hidsc': ''
        }
        #登陆教务系统
        response = self.session.post(self.login,data=data)
        print("验证码识别成功！")
        print("成功进入教务系统！")
        self.getName(response)

    #查等级考试成绩
    def getLevel(self):
        referer = self.checkNo
        referer = referer.format(username=self.student.number)
        headers = self.session.headers
        headers['referer'] = referer
        checkLevel = self.checkLevel.format(username=self.student.number, name=self.student.name)
        Response = self.session.post(checkLevel, headers=headers)
        html = Response.content.decode("gb2312")
        with open('./html/Level.html', 'w') as f:
            f.write(str(html))
        print("等级考试成绩查询成功！")

    #查课表
    def getTimetable(self):
        referer = self.checkNo
        referer = referer.format(username=self.student.number)
        headers = self.session.headers
        headers['referer'] = referer
        checkTimetable = self.checkTimetable.format(username=self.student.number, name=self.student.name)
        Response = self.session.post(checkTimetable, headers=headers)
        html = Response.content.decode("gb2312")
        with open('./html/Timetable.html', 'w') as f:
            f.write(str(html))
        print("课表查询成功！")

    # 个人信息
    def getInfo(self):
        info = self.checkInfo.format(username=self.student.number, name=self.student.name)
        headers = self.session.headers
        headers['referer'] = info
        Response = self.session.post(info, headers=headers)
        html = Response.content.decode("gb2312")
        with open('./html/Info.html', 'w') as f:
            f.write(str(html))
        print("个人信息查询成功！")
        html = etree.HTML(html)
        idcard = html.xpath("//table[@class='formlist']/tr[11]/td[4]/span/text()")
        highschool = html.xpath("//table[@class='formlist']/tr[5]/td[4]/span/text()")
        try:
            print("身份证号："+idcard[0])
            print("毕业中学："+highschool[0])
        except IndexError as e:
            print(e)


    # 查所有成绩
    def getReport(self):
        referer = self.checkNo
        referer = referer.format(username=self.student.number)
        headers = self.session.headers
        headers["Referer"] = referer
        url = self.checkScore
        url = url.format(username=self.student.number, name=self.student.name)

        ResponseTest = self.session.get(url, headers=headers).text
        soup = BeautifulSoup(ResponseTest, 'lxml')
        __VIEWSTATE = soup.find_all('input')[2]['value']
        postdata = {
            '__EVENTTARGET': '',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': '',
            'hidLanguage': '',
            'ddlXN': '',  # 学年
            'ddlXQ': '',  # 学期
            'ddl_kcxz': '',  # 课程选择
            'btn_zcj': '',  # 历年成绩
        }
        postdata['__VIEWSTATE'] = __VIEWSTATE
        postdata['btn_zcj'] = '历年成绩'.encode('gb2312')
        Response = self.session.post(url, data=postdata, headers=headers)
        html = Response.content.decode("gb2312")
        with open('./html/Report.html', 'w') as f:
            f.write(str(html))
        print("历年成绩查询成功！")

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    user = input("学号：")     # 输入学号
    pwd = getpass("密码：")    # 隐式输入密码
    student = Student(user, pwd) # 参数 学号 密码
    spider = CsuftJwc(student, ip="210.43.247.44")  # 实例化爬虫
    spider.Login()
    if spider.Yes():
        spider.getInfo()
        spider.getReport()
        spider.getTimetable()
        spider.getLevel()
