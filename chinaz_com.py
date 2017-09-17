#coding:utf-8
from bs4 import BeautifulSoup as bs
import requests
import pm as pm
import json
import time
import re
import sys

#config配置
list = {'extension':1,'product':2,'design':3}
if len(sys.argv)>1:
    config = sys.argv[1]
    category = str(list[sys.argv[1]])
else:
    config = 'extension'
    category = '1';

#处理url
if config == "extension":
    link = "http://www.chinaz.com/manage/extension/"
elif config == "product":
    link = "http://www.chinaz.com/manage/product/"
elif config == "design":
    link = "http://www.chinaz.com/design/"
ip = "10.12.345.892"
headers={"CLIENT-IP":ip,"X-FORWARDED-FOR":ip}
response = requests.get(link,headers=headers)
#html = response.text
html = response.text.encode(response.encoding).decode('utf-8')
soup = bs(html,"html.parser")
list = soup.find_all("div",{"class":"catlist-box"});
now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
table = "cmf_posts"
fromKey='chinaz'
#图片保存路径
picSavePath = '/home/wwwroot/www.51bamin.com/Uploads/collect/'
#图片读取路径
picReadPath = 'https://www.51bamin.com/Uploads/collect/'
def start():
    for data in list:
        detailLink = data.find("h4").find("a").get('href')
        #正则匹配获取唯一标识
        m = re.match(r'.*/(\d*/\d*/\d*)', detailLink)
        mArr = m.groups()
        id = mArr[0]  #唯一标识
        if pm.getcount(table,{'fromID':id,'fromKey':fromKey})==0:
            row = {}
            row["post_title"] = data.find("h4").find("a").get_text()
            isThumb = data.find("div", {"class": "img-do"})
            if isThumb== None:
                dataBasePath = ''
            else:
                thumImg = data.find("div", {"class": "img-do"}).find("img").get('src')
                thumImg = pm.saveFile(thumImg, picSavePath)
                dataBasePath = picReadPath+thumImg

            aa = '{"thumb": "'+dataBasePath+'", "template": "", "photo": ""}'
            row['smeta'] = aa
            row['post_date'] = now
            row['post_modified'] = now
            row['fromKey']=fromKey
            row['fromID'] = id
            row['post_author']='1'
            row['term_id'] = category
            id = pm.insert(table, row)
            updateDetail(detailLink, id)
def updateDetail(link,id):
    sys.setrecursionlimit(1000000)
    detail_repose = requests.get(link, headers=headers)
    #detail_html = detail_repose.text
    detail_html = detail_repose.text.encode(detail_repose.encoding).decode('utf-8')
    detail_soup = bs(detail_html, "html.parser")
    data = {}
    map = {}
    content = detail_soup.find("div",{"class":"detail"})
    desc = content.get_text()
    desc = desc[0:70]
    imgList=content.find_all('img')
    for row in imgList:
        srcPath = row.get("src")
        if srcPath!=None:
            tag = content.find("img",{"src":srcPath})
            # 图片保存路径
            ret = pm.saveFile(srcPath,picSavePath)
            tag['src'] = picReadPath+ret
            tag['srcset'] = picReadPath+ret
    data["post_content"] = str(content)
    data['post_excerpt'] = desc
    map['id'] = id
    pm.update(table,map,data)


