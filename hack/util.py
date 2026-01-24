# coding=utf-8
import subprocess
import pymongo
import sys
import datetime
import os
# "%Y-%m-%d %H:%M:%S"
def isNull(obj):
    if obj is None:
        return True
    if obj=="":
        return True
    return False

def getKeys_dic(obj,keys=[]):

    result={}
    if obj is None:
        return None
    for key in keys:
        result[key]=obj[key]
    if len(result.keys())==0:
        return None
    return result

# 杀死进程
def kill_port(port):
    resu = subprocess.Popen("lsof -i:" + str(port), shell=True, stdout=subprocess.PIPE)
    resu.wait()
    result = resu.stdout.read()
    if result is None or result == b'':
        return
    print('kill_port', result)
    result = str(result, encoding='gbk')
    lis = result.split('\n')
    # 删除 空白字符
    for i in range(len(lis)):
        lis[i] = lis[i].split(' ')
        removeNum = 0
        for l in range(len(lis[i])):
            if lis[i][l - removeNum] == '':
                lis[i].pop(l - removeNum)
                removeNum += 1
    print(lis)

    pid_index = lis[0].index('PID')
    resu = subprocess.Popen('kill -9 ' + lis[1][pid_index], shell=True, stdout=subprocess.PIPE)
    resu.wait()


def mongodb_connect():

    mongo_ip = ['101.35.44.243', '127.0.0.1']
    root = 'myUserAdmin'
    password = 'abc123'
    # systemctl restart mongod
    # myclient = pymongo.MongoClient("mongodb://{}:{}@{}:27017/".format(root, password, mongo_ip[1]))
    myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
    # try:
    #     env_ = sys.argv[1]
    #     if env_ == 'SERVER':
    #         print('connect:', env_)
    #         myclient = pymongo.MongoClient("mongodb://{}:{}@{}:27017/".format(root, password, mongo_ip[0]))
    #     else:
    #         myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
    # except Exception as e:
    #     myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
    # print(myclient['dongfangcaifu'])
    return myclient

def build_date(now=datetime.datetime.now(), add_month=0, add_day=0):
    print(type(now))
    if isinstance(now, str):
        now = datetime.strptime(now, '%Y-%m-%d')
    month = now.month + add_month
    year_ = int(month/12)
    month = month%12
    if month == 0:
        year_ -=1
        month = 12
    result = datetime.datetime(year=now.year+year_, month=month, day=now.day)
    timestamp = result.timestamp() + now.timestamp()%24*60*60 + add_day*24*60*60
    return datetime.datetime.fromtimestamp(timestamp)


if __name__ == '__main__':
    print(sys.argv)
    # mongodb_connect()
    print(build_date(add_day=30))
