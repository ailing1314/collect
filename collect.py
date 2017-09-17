#coding:utf-8
from bs4 import BeautifulSoup as bs
import requests
import pm as pm
import json
import time
import re
import sys

#config配置
list = {'it':1,'pd':2,'ucd':3,'zhichang':4,'b2b':5,'report':6,'youqu':7}
if len(sys.argv)>1:
    config = sys.argv[1]
    category = str(list[sys.argv[1]])
else:
    config = 'it'
    category = '1';


link="http://www.yixieshi.com/"+config
ip = "10.12.345.892"
headers={"CLIENT-IP":ip,"X-FORWARDED-FOR":ip}
response = requests.get(link,headers=headers)
html = response.text
soup = bs(html,"html.parser")
list = soup.find_all("div",{"class":"article-box"});
now = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
table = "cmf_posts"
fromKey='hlwyxs'
#图片保存路径
picSavePath = '/home/wwwroot/www.51bamin.com/Uploads/collect/'
#图片读取路径
picReadPath = 'https://www.51bamin.com/Uploads/collect/'
def start():
    for data in list:
        detailLink = data.find("h2").find("a").get('href')
        print(detailLink)
        #正则匹配获取唯一标识
        m = re.match(r'[\./:a-zA-Z]*(\d*)\.[a-z]*', detailLink)
        mArr = m.groups()
        id = mArr[0]  #唯一标识
        if pm.getcount(table,{'fromID':id,'fromKey':fromKey})==0:
            row = {}
            row["post_title"] = data.find("h2").get_text()
            if data.find("p", {"class": "txtcont"}).script:
                data.find("p", {"class": "txtcont"}).script.decompose()
            if data.find("p", {"class": "txtcont"}).span:
                data.find("p", {"class": "txtcont"}).span.decompose()
            row["post_excerpt"] = data.find("p", {"class": "txtcont"}).find("a").get_text()
            thumImg = data.find("div", {"class": "thumbnail"}).find("img").get("src")
            thumImg = pm.saveFile(thumImg,picSavePath)
            aa = '{"thumb": "'+picReadPath+thumImg+'", "template": "", "photo": ""}'
            row['smeta'] = aa
            row['post_date'] = now
            row['post_modified'] = now
            row['fromKey']=fromKey
            row['fromID'] = id
            row['post_author']='1'
            row['term_id'] = category
            id = pm.insert(table, row)
            exit()
            updateDetail(detailLink, id)
def updateDetail(link,id):
    sys.setrecursionlimit(1000000)
    detail_repose = requests.get(link, headers=headers)
    detail_html = detail_repose.text
    detail_soup = bs(detail_html, "html.parser")
    data = {}
    map = {}
    content = detail_soup.find("article",{"class":"article-content"})
    if content.script:
        content.script.decompose()
    #去掉敏感标记内容
    if content.find_all('p', string=re.compile('互联网的一些事')):
        for pword in content.find_all('p', string=re.compile('互联网的一些事')):
            pword.decompose()
    if content.find_all('a', href=re.compile('http://www.yixieshi.com')):
        for pword_link in content.find_all('a', href=re.compile('http://www.yixieshi.com')):
            pword_link.parent.decompose()
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
    map['id'] = id
    pm.update(table,map,data)

