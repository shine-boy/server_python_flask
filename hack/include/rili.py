import requests
from datetime import datetime
import json

# 日历
def getToday():
    now=datetime.now()
    path="%d/%02d%02d.js?_=%d"%(now.year,now.month,now.day,now.timestamp() * 1000)

    res = requests.get(url="https://www.rili.com.cn/rili/json/today/"+path)

    data=json.loads(res.text[14:-2])
    return data

def getOneday(day=datetime.now()):

    path="%d/%02d%02d.js?_=%d"%(day.year,day.month,day.day,day.timestamp() * 1000)

    res = requests.get(url="https://www.rili.com.cn/rili/json/today/"+path)

    data=json.loads(res.text[14:-2])
    return data

def getMonth(year=None,month=None):
    now = datetime.now()
    if year is None:
        year=now.year
    if month is None:
        month=now.month
    path = "%d/%02d.js?_=%d" % (year, month, now.timestamp() * 1000)
    res = requests.get(url="https://www.rili.com.cn/rili/json/pc_wnl/" + path)
    data = json.loads(res.text[14:-7])
    return data

# 是否是工作日
def isWork(day=datetime.now()):
    data=getMonth()
    for da in data['data']:
        if da['yue']==day.month and da['ri']==day.day:
            # jia >90 :休息， jia==90 上班
            if da['jia']==90:
                return True
            if day.isoweekday()<6:
                return True
    pass
    return False

# 判断是否是股票交易日
def isStockDeal(day=datetime.now()):
    data=getMonth()
    for da in data['data']:
        if da['yue']==day.month and da['ri']==day.day:
            # jia >90 :休息， jia==90 上班
            if day.isoweekday()<6 and da['jia']<90:
                return True
    return False
