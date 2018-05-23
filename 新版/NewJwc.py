import requests
import importlib
import time
from bs4 import BeautifulSoup
import sys
import os
from getpass import getpass
from mail import SendEmail

class Student:
    def __init__(self , number , password):
        self.name = ''
        self.number = number
        self.password = password

class CsuftJwc:
    def __init__(self, student):
        importlib.reload(sys)
        #初始参数
        self.host = "http://jwgl.csuft.edu.cn"
        self.login = "http://authserver.csuft.edu.cn/authserver/login?service=http%3A%2F%2Fjwgl.csuft.edu.cn%2F"    # 教务处统一身份认证入口
        self.checkScore = "http://jwgl.csuft.edu.cn/jsxsd/kscj/cjcx_frm"
        self.checkLevel = self.host+'/jsxsd/kscj/djkscj_list'
        self.student = student
        self.session = requests.session()
        self.session.headers = {
            "Referer": "http://authserver.csuft.edu.cn/authserver/login?service=http%3A%2F%2Fjwgl.csuft.edu.cn%2F",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        }
        self.message = ""      # 成绩单信息
        self.root = './html/'
        if not os.path.exists(self.root):
            os.mkdir(self.root)

    def show(self,trs):
        for tr in trs:
            for td in tr:
                s = td.string
                if s and s != "\n":
                    print(s,end=' ')
                    self.message += s+' '
            print()
            self.message += '\n'

    def getName(self, response):
        html = response.content.decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        body = soup.body
        Nsb_pw = body.find('div', attrs={'class': 'Nsb_pw'})
        Nsb_top = Nsb_pw.find('div', attrs={'class': 'Nsb_top'})
        Nsb_top_menu = Nsb_top.find('div', attrs={'class': 'Nsb_top_menu'})
        text = (str(Nsb_top_menu.find('div', attrs={'class': 'Nsb_top_menu_nc'})).split("\">")[1][0:2])
        self.student.name = text
        print("欢迎"+text+"同学!\n")

    def Login(self):
        # 访问教务系统
        response = self.session.get(self.login)
        str = response.content.decode("utf-8")
        lt = str[str.find("name=\"lt\" value=\""):str.find("-49sC-cas")].replace("name=\"lt\" value=\"","")+"-49sC-cas"
        # 构造登录数据
        data = {
            'username': self.student.number,
            'password': self.student.password,
            'lt':lt,
            'dllt':'userNamePasswordLogin',
            'execution':'e1s1',
            '_eventId':'submit',
            'rmShown':'1'
        }
        #登陆教务系统
        response = self.session.post(self.login,data=data)
        if response.status_code == 200:
            print("成功进入教务系统！")
        self.getName(response)

    # 查本学期成绩
    def getReport(self):
        print("本学期成绩：",end='')
        cjcx = self.session.post(self.checkScore).content.decode("utf-8")
        str = cjcx[cjcx.find("cjcx_list_frm")+41:cjcx.find("cjcx_list_frm")+79]
        html = self.session.post(self.host+str).content
        with open(self.root+'本学期成绩.html', 'wb') as f:
            f.write(html)
        soup = BeautifulSoup(html,"lxml").find('div', attrs={'class': 'Nsb_pw Nsb_pw1'})
        trs = soup.find_all("tr")
        self.show(trs)

    #查等级考试成绩
    def getLevel(self):
        print("等级考试成绩：")
        html = self.session.post(self.checkLevel).content
        with open(self.root+'等级考试成绩.html', 'wb') as f:
            f.write(html)
        soup = BeautifulSoup(html, "lxml").find('div', attrs={'class': 'Nsb_layout_r'})
        trs = soup.find_all("tr")
        self.show(trs)

if __name__ == "__main__":
    user = input("学号：")     # 输入学号
    pwd = getpass("密码：")    # 隐式输入密码
    oldReportlen = 150         # 已经查看过的成绩的字符串长度
    student = Student(user, pwd)
    while True:               # 不断循环监控是否有新成绩
        spider = CsuftJwc(student)  # 实例化爬虫
        spider.Login()
        spider.getReport()
        if len(spider.message)>oldReportlen:    # 出了新成绩就立刻把新的成绩单写成邮件发给自己
            SendEmail(spider.message)           # 发邮件
            print("出新成绩了")
            break
        print("监控中...")
        time.sleep(60)                          # 1分钟检测一次，防止太快了锁IP
