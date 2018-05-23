#-*-coding:utf-8-*-
import requests
import os

end = 500
for i in range(1,end+1):
    session = requests.session()
    session.headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36",
    }
    imgUrl = "http://jw.hzau.edu.cn/CheckCode.aspx???????"
    imgresponse = session.get(imgUrl, stream=True)
    pic = imgresponse.content
    root  = './/checkcode//'
    if not os.path.exists(root):
        os.mkdir(root)
    with open(root+str(i)+'.png', 'wb') as f:
        f.write(pic)
        f.close()
    print(str(i)+'.png保存成功.')