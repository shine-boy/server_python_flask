
import subprocess
import pymongo
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

# É±ËÀ½ø³Ì
def kill_port(port):
    resu = subprocess.Popen("lsof -i:" + port, shell=True, stdout=subprocess.PIPE)
    resu.wait()
    result = resu.stdout.read()
    if result is None or result == b'':
        return
    print(result)
    result = str(result, encoding='gbk')
    lis = result.split('\n')
    # É¾³ý ¿Õ°××Ö·û
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
    myclient = pymongo.MongoClient("mongodb://{}:{}@{}:27017/".format(root, password, mongo_ip[1]))
    # myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
    return myclient