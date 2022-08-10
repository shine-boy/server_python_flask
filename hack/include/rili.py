import requests
from datetime import datetime
import json
import chinese_calendar
# 日历
def getToday(now=datetime.now()):

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
    print(year, month)
    path = "%d/%02d.js?_=%d" % (year, month, now.timestamp() * 1000)
    res = requests.get(url="https://www.rili.com.cn/rili/json/pc_wnl/" + path)
    print(res.text)
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
# 不是工作日且不休息
def isStockDeal(day=datetime.now()):
    return chinese_calendar.is_workday(day) and day.isoweekday()<6
    # data=getMonth(day.year, day.month)
    # for da in data['data']:
    #     if da['yue']==day.month and da['ri']==day.day:
    #         # jia >90 :休息， jia==90 上班
    #         if day.isoweekday()<6 and da['jia']<90:
    #             return True
    # return False


# 获取最近limit股票交易日
def stock_days(limit, now=datetime.now()):
    i = 0
    days = []
    while i < limit:
        timestamp = i*24*60*60
        cur = datetime.fromtimestamp(now.timestamp() - timestamp)
        if isStockDeal(cur) is False:
            limit += 1
            i += 1
            continue
        temp_time = datetime(year=cur.year, month=cur.month, day=cur.day)
        i+=1
        days.append(temp_time)
    return days