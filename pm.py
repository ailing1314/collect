#coding:utf-8
import pymysql.cursors
import requests
import time
import random
import os
connection = pymysql.connect(host='localhost',user='root',password='123456',db='dayu',charset='utf8')
def setUtf8():
    with connection.cursor() as cursor:
        cursor.execute("set names utf8")
#######################插入数据#####################################
def insert(table,row):
    field = ""
    data = ""
    i = 0
    for key in row:
        pre = ","
        if i == 0:
            pre = ""
        field += pre+"`"+key+"`"
        data += pre+"'"+row[key]+"'"
        i = i+1
    with connection.cursor() as cursor:
        # 创建sql语句
        #sql = "insert into `test` (name) values(%s)"
        sql = "insert into " + table + " (" + field + ") values("+data+")"
        # 执行mysql语句
        #cursor.execute("set names gbk")
        cursor.execute(sql)
        lastID = connection.insert_id()
        # 提交
        connection.commit()
    return lastID
###########################更新数据##############################
def update(table,map,row):
    where = ""
    data = ""
    i = 0
    for key in row:
        pre = ","
        if i == 0:
            pre = ""
        data += pre+key+"='"+str(row[key])+"'"
        i = i+1
    if isinstance(map, dict):
        i = 0
        for key in map:
            preWhere = "AND"
            if i == 0:
                preWhere = " WHERE "
            where += preWhere + " " + key + "='"+str(map[key])+"'"
            i = i + 1
    else:
        if where!="":
             where = "WHERE "+map
    # 获取会话指针
    with connection.cursor() as cursor:
        # 创建sql语句
        sql = "update " + table + "  SET  "+data+"  "+where
        # 执行mysql语句
        cursor.execute(sql)
        lastID = connection.insert_id()
        # 提交
        connection.commit()
    return lastID

#######获取数据条数#############################
def getcount(table,map):
    where = ""
    i = 0
    if isinstance(map, dict):
        i = 0
        for key in map:
            preWhere = "AND"
            if i == 0:
                preWhere = "WHERE "
            where += preWhere + " " + key + "='"+str(map[key])+"'"
            i = i + 1
    else:
        if where!="":
             where = "WHERE "+map
    # 获取会话指针
    with connection.cursor() as cursor:
        # 创建sql语句
        sql = "SELECT count(*) FROM " + table+" "+where
        # 执行mysql语句
        cursor.execute(sql)
        res = cursor.fetchone()
        count=res[0]
        # 提交
        connection.commit()
    return count

def saveFile(path,saveRootPath="./"):
    response = requests.get(path)
    fileName = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))+"xiake"+str(random.randint(1000, 9999))
    #ext = os.path.splitext(path)[1]  #后缀名
    ext = ".jpg"
    datePath=time.strftime('%Y',time.localtime(time.time()))+"/"+time.strftime('%m',time.localtime(time.time()))+"/"+time.strftime('%d',time.localtime(time.time()))+"/"
    savePath = saveRootPath+datePath
    if os.path.exists(savePath) != True:
        os.makedirs(savePath)
    saveName = savePath+fileName+ext
    with open(saveName, 'wb') as fd:
        for chunk in response.iter_content(128):
            fd.write(chunk)
    return datePath+fileName+ext








