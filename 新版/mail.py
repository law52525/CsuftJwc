from aifc import Error
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.header import Header
from smtplib import *

def SendEmail(messages):
    # content为邮件正文内容，title为邮件标题
    content = {'content': messages, 'title': '成绩单'}
    # qq邮箱smtp服务器
    host_server = 'smtp.qq.com'
    # sender_qq为发件人的qq号码
    sender_qq = '**********'
    # pwd为qq邮箱的应用专有授权码
    pwd = '**************'
    # 发件人的邮箱
    sender_qq_mail = sender_qq+'@qq.com'
    # 收件人邮箱
    receiver = 'test@example.com'
    # 邮件的正文内容
    mail_content = content['content']
    # 邮件标题
    mail_title = content['title']

    msg = MIMEMultipart()
    msg["Subject"] = Header(mail_title, 'utf-8')
    msg["From"] = sender_qq_mail
    msg["To"] = receiver
    text = MIMEText(mail_content, "plain", 'utf-8')
    msg.attach(text)
    print("正文完成！")
    # 附件
    # fn = "Level.html"
    # part = MIMEApplication(open(fn, 'rb').read())
    # part.add_header("Content-Disposition", "attachment", filename=fn)
    # msg.attach(part)
    # fn = "Report.html"
    # part = MIMEApplication(open(fn, 'rb').read())
    # part.add_header("Content-Disposition", "attachment", filename=fn)
    # msg.attach(part)
    # fn = "Timetable.html"
    # part = MIMEApplication(open(fn, 'rb').read())
    # part.add_header("Content-Disposition", "attachment", filename=fn)
    # msg.attach(part)
    # print("附件添加成功！")

    # ssl登录
    try:
        smtp = SMTP_SSL(host_server)
        smtp.login(sender_qq, pwd)
        print("登录成功！")
        smtp.sendmail(sender_qq_mail, receiver, msg.as_string())
        print("邮件已投递！")
        smtp.quit()
    except Error as e:
        print(e)
