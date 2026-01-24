# coding=utf-8
import datetime
import os
import sys

# linux下包导入失败
path = os.path.abspath('./..')
sys.path.append('/home/gitlab-runner/builds/NsGaLx8a/0/root/server_python_flask')  # 会追加到列表最尾部
print('os.getcwd():', os.getcwd())
sys.path.append(os.getcwd())  # 会追加到列表最尾部

from hack.util import kill_port
from hack.include.timeManager import TimeManager
import threading
from wsgiref.simple_server import make_server
import json
import math
from hack.include import Stock,Page
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import time
from flask import Flask, request
import hack.include.rili as rili
from hack.servers_api import StockApi, FundApi, JournalApi, OtherApi
from hack.stock import Statistic
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_MIMETYPE'] = "application/json;charset=utf-8"
sched = BackgroundScheduler()

def job(name):
    # sys.path.append('/home/gitlab-runner/builds/tYTjy6R-/0/root/server_python_flask')  # scrapy脚本執行
    os.system("cd /home/gitlab-runner/builds/tYTjy6R-/0/root/server_python_flask && scrapy crawl "+name)

def doWeek(lis):
    for i in lis:
        threading.Thread(target=job,args=(i,)).start()
    pass

# 获取重启后的首次执行时间
def getStartTime(startTime,day=0,hours=0,minute=0,second=0):
    today = datetime.datetime.today()
    if startTime > today:
        return startTime
    interval=(second+60*(minute+60*(hours+day*24)))
    if interval==0:
        interval=1
    print(interval)
    space=today.timestamp() - startTime.timestamp()
    print(space)
    print(math.ceil(space/interval))
    result=interval*math.ceil(space/interval)+startTime.timestamp()
    return datetime.datetime.fromtimestamp(result)

def dowangyiyun():
    print('rere')
    # os.system("cd E:\git\/bigData && scrapy crawl wangyiyun")
    job('wangyiyun')

# 基金
def dofund():
    print('rere')
    if not rili.isStockDeal():
        return
    # os.system("cd E:\git\/bigData && scrapy crawl wangyiyun")
    job('dfcf_fund')

def dongfangcaifu():
    if not rili.isStockDeal():
        return
    stock = Stock()
    times = ['9:30', "11:31", "13:00", '15:01']
    now = datetime.datetime.now()
    for i in range(len(times)):
        temp = times[i].split(":")
        times[i] = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=int(temp[0]),
                                     minute=int(temp[1]))

    def test():
        print('time')
        # os.system("scrapy crawl dongfangcaifu")
        ti=time.time()
        stock.do(stock.insert_mongo)
        stock.waiter()
        print(time.time()-ti)
    for i in range(0, len(times), 2):
        if times[i+1] < now:
            continue
        if times[i] < now:
            times[i] = datetime.datetime(year=now.year, month=now.month, day=now.day, hour=now.hour,
                                         minute=now.minute+1)
        sched.add_job(test, 'interval', minutes=2, end_date=times[i + 1], start_date=times[i],max_instances=10,misfire_grace_time=3600)
    # os.system("cd E:\git\/bigData && scrapy crawl dongfangcaifu")

# @sched.scheduled_job('cron',day_of_week="0-4",misfire_grace_time=3600)
def do_dongfangcaifu():
    dongfangcaifu()

def doSched():
    print('start')
    print(datetime.datetime.now())
    statistic = Statistic()
    schedList = {
        '网易云':{
            'func': dowangyiyun,
            'args': {
                'type': 'interval',
                'days': 7,
                'misfire_grace_time': 3600,
                'start_date': getStartTime(datetime.datetime(2021, 2, 2, 18, 0, 0),day=7)
            }
        },
        '基金': {
            'func': dofund,
            'args': {
                'type': 'cron',
                'day_of_week': "0-4",
                'misfire_grace_time': 3600,
                'hour': '19'
            }
        },
        '东方财富': {
            'func': do_dongfangcaifu,
            'args': {
                'type': 'cron',
                'day_of_week': "0-4",
                'misfire_grace_time': 3600,
                'hour': '8'
            }
        },
        '股票统计': {
            'func': statistic.calculate,
            'args': {
                'type': 'cron',
                'day_of_week': "0-4",
                'misfire_grace_time': 3600,
                'hour': '18'
            }
        },
        '股票汇总': {
            'func': statistic.updateToday,
            'args': {
                'type': 'cron',
                'day_of_week': "0-4",
                'misfire_grace_time': 3600,
                'hour': '19'
            }
        }
    }
    timeManager = TimeManager()
    for key in schedList.keys():
        timeManager.run(key, schedList[key]['func'], schedList[key]['args'])
    # threading.Thread(target=dongfangcaifu).start()
    sched.start()


@app.before_request
def before_first_request():
    pass
    # data={"cmd":"scrapy crawl wangyiyun"}
    # threading.Thread(target=cmd_job, args=(data,)).start()
    # print('start')
    # threading.Thread(target=doSched).start()


def cmd_job(data):
    print("start%s"%data.get("url"))
    time.sleep(60)
    if data.get("url"):
        os.chdir(data.get("url"))
    if data.get("cmd"):
        time.sleep(60)
        os.system(data.get("cmd"))


@app.route('/runcmd', methods=['POST','GET'])
def runcmd():
    if request.method == 'POST':
        data = json.loads(request.data)
    else:
        data = request.args

    threading.Thread(target=cmd_job,args=(data,)).start()
    return ""



# schedule.every().wednesday.at("15:50").do(doWeek,wednesdayList)
# schedule.every().thursday.at("15:50").do(doWeek,thursdayList)
# schedule.every().day.at("20:00").do(doEvery)
# schedule.every().day.at("09:58").do(servers_api)
if __name__ == '__main__':
    stockApi = StockApi(app)
    fundApi = FundApi(app)
    journalApi = JournalApi(app)
    otherApi = OtherApi(app)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    port = 9988
    kill_port(port)
    time.sleep(3);
    # threading.Thread(target=doSched).start()
    server = make_server('0.0.0.0', port, app)
    print('run: 0.0.0.0:' + str(port))
    server.serve_forever()

    # pass
