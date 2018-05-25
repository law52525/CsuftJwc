import requests
import importlib
from lxml import etree
import sys
import os
from mail import SendEmail
from getpass import getpass

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
        self.checkNow = self.host+'/jsxsd/kscj/cjcx_frm'
        self.checkLevel = self.host+'/jsxsd/kscj/djkscj_list'
        self.checkAll = self.host+'/jsxsd/kscj/cjcx_list'
        self.student = student
        self.session = requests.session()
        self.session.headers = {
            "Referer": "http://authserver.csuft.edu.cn/authserver/login?service=http%3A%2F%2Fjwgl.csuft.edu.cn%2F",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
        }
        self.root = './data/'
        if not os.path.exists(self.root):
            os.mkdir(self.root)

    def getName(self, response):
        html = etree.HTML(response.content.decode("utf-8"))
        text = html.xpath("//div[@id='Top1_divLoginName']/text()")[0].split("(")[0]
        self.student.name = text
        print("欢迎"+text+"同学!")

    def Login(self):
        # 访问教务系统
        response = self.session.get(self.login)
        html = etree.HTML(response.content.decode("utf-8"))
        lt = html.xpath("//form[@id='casLoginForm']/input[@name='lt']/@value")
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

    def ShowAndSave(self,ret,type):
        print(type+"：")
        with open(self.root+self.student.name+type+".txt","w",encoding="utf-8") as f:
            for i in ret:
                print(i)
                f.write(i+"\n")
        f.close()

    # 查本学期成绩
    def getNow(self):
        html = self.session.post(self.checkNow).content
        html = etree.HTML(html.decode("utf-8"))
        time = html.xpath("//div[@class='Nsb_r_title']/text()")[0].split("询")[1]
        data = self.getchoice(time)
        self.ShowAndSave(data,"本学期成绩")

    # 查等级考试成绩
    def getLevel(self):
        ret = []
        html = self.session.post(self.checkLevel).content
        html = etree.HTML(html.decode("utf-8"))
        th = html.xpath("//table[@class='Nsb_r_list Nsb_table']/tr/th/text()")
        th = th[0:2]+th[-3:]+[th[4]]
        ret.append(' '.join(th))
        tr = html.xpath("//table[@class='Nsb_r_list Nsb_table']/tr")
        tr_len = len(tr)
        for i in range(3,tr_len+1):
            r = html.xpath("//table[@class='Nsb_r_list Nsb_table']/tr[" + i.__str__() + "]/td/text()")
            ret.append(' '.join(r))
        self.ShowAndSave(ret,"等级考试成绩")

    # 查全部成绩
    def getAll(self):
        data = self.getchoice("")
        self.ShowAndSave(data,"全部成绩")


    # 根据开课时间查询成绩
    def getchoice(self,kksj):
        ret = []
        data = {
            'kksj':kksj,
            'kcxz':'',
            'kcmc':'',
            'xsfs':'all'
        }
        html = self.session.post(self.checkAll,data=data).content
        html = etree.HTML(html.decode("utf-8"))
        th = html.xpath("//table[@class='Nsb_r_list Nsb_table Nsb_table_first']/tr[@class='tr2']/th/text()")
        ret.append(' '.join(th))
        tr = html.xpath("//table[@class='Nsb_r_list Nsb_table']/tr")
        tr_len = len(tr)
        for i in range(1,tr_len+1):
            r = html.xpath("//table[@class='Nsb_r_list Nsb_table']/tr["+ i.__str__() +"]/td/text()")
            score = html.xpath("//table[@class='Nsb_r_list Nsb_table']/tr["+ i.__str__() +"]/td/a/font/text()")
            ret.append(' '.join(r[0:4]+score+r[4:]))
        return ret

    # 发邮件
    def SendMail(self):
        self.getNow()
        with open(self.root + self.student.name + "本学期成绩" + ".txt", "r", encoding="utf-8") as f:
            data = f.readlines()
        SendEmail(''.join(data))

if __name__ == "__main__":
    user = input("学号：")               # 输入学号
    pwd = getpass("密码：")              # 隐式输入密码
    student = Student(user, pwd)
    spider = CsuftJwc(student)           # 实例化爬虫
    spider.Login()                       # 登录教务系统
    spider.getNow()                      # 获取本学期成绩
    spider.getLevel()                    # 获取等级考试成绩
    spider.getAll()                      # 获取全部成绩
    # spider.SendMail()                    # 把成绩单通过邮件发出去
