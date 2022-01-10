# coding=utf-8
import datetime
import os
import sys

# linux下包导入失败
# path = os.path.abspath('./..')
sys.path.append('/home/gitlab-runner/builds/tYTjy6R-/0/root/server_python_flask')  # 会追加到列表最尾部
import hack.include.excel as myExcel
from hack.util import isNull, kill_port
import pymongo
from hack.include.timeManager import TimeManager
import threading
from wsgiref.simple_server import make_server
import json
import math
from hack.include import Stock,Page
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import time
from flask import Response, Flask, request, make_response
from flask_cors import CORS
import hack.include.rili as rili
app = Flask(__name__)
myclient = pymongo.MongoClient("mongodb://127.0.0.1:27017/")
mydb = myclient["local"]
projectExam=myclient["projectExam"]
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
    print('tests')

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

@sched.scheduled_job('cron',day_of_week="0-4",misfire_grace_time=3600)
def do_dongfangcaifu():
    dongfangcaifu()

def doSched():
    print('start')
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
        }
    }
    timeManager = TimeManager()
    for key in schedList.keys():
        timeManager.run(key, schedList[key]['func'], schedList[key]['args'])
    # threading.Thread(target=dongfangcaifu).start()
    # sched.start()


@app.before_first_request
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

CORS(app,resources=r"/*")
@app.route('/deleteWangyiyun', methods=['POST','GET'])
def deleteWangyiyun():
    if request.method == 'POST':
        if request.data:
            data = json.loads(request.data)
        else:
            data=request.form
    else:
        data = request.args
    comments = mydb["comments"]
    
    query = {'id':data["id"]}
    comments.delete_one(query)
    response=Response()
    response.headers={"Access-Control-Allow-Origin":"*"}
    response.data=json.dumps({'data':"success"})
    return response

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)

CORS(app,resources=r"/*")
@app.route('/wangyiyun', methods=['POST','GET'])
def seachWangyiyun():
    if request.method == 'POST':
        if request.data:
            data = json.loads(request.data)
        else:
            data=request.form
    else:
        data = request.args
    page=Page(data.get("page")).page

    comments = mydb["comments"]
    query = {"comments.likedCount":{"$gt":2}}
    sort=[]
    sortType = data.get("sort")
    if sortType is None:
        sort=[("comments.likedCount", -1)]
    else:
        sort=[(sortType,-1)]
    lis = comments.find(query, { "_id":0}).sort(sort).limit(page.get("pageSize")).skip(page.get("pageSize")*(page.get("current")-1))
    lis = list(lis)
    #
    result={
        'data':lis,
        'total':comments.estimated_document_count()
    }
    print(len(lis))
    response=Response()
    response.headers={"Access-Control-Allow-Origin":"*"}
    response.data=json.dumps(result,cls=DateEncoder)
    return response

CORS(app,resources=r"/*")
@app.route('/projectExam', methods=['POST','GET'])
def seachprojectExam():
    if request.method == 'POST':
        if request.data:
            data = json.loads(request.data)
        else:
            data=request.form
    else:
        data = request.args
    page=Page(data.get("page")).page
    type_=data.get("questionType","choice")
    comments = projectExam[type_]
    query = {}
    if isNull(data.get("content")) is False:
        query['content']={'$regex':".*"+data.get("content")+".*"}
    if isNull(data.get("type")) is False:
        query['type']={'$regex':".*"+data.get("type")+".*"}
    print(page)
    lis = comments.find(query,{"_id":0}).limit(page.get("pageSize")).skip(page.get("pageSize")*(page.get("current")-1))
    lis = list(lis)
    #
    # print(comments.count_documents(filter=query))
    result = {
        'data': lis,
        'total': comments.count_documents(filter=query)
    }
    response=Response()
    response.headers={"Access-Control-Allow-Origin":"*"}
    response.data=json.dumps(result)
    return response

@app.route('/uploadProjectExel', methods=['POST'])
def uploadProjectExel():
    try:
        my_file = request.files['file']
        # print(my_file)
        data = None
        if request.form:
            data = request.form.to_dict()

        if data and data.get('type') == '1':
            resfile = myExcel.jibing(my_file, head=data.get('header'), filter=data.get('filter'))
        else:
            resfile = myExcel.waike(my_file, head=data.get('header'), filter=data.get('filter'))
    except Exception as e:
        print(e)
        pass
    response = Response(resfile)

    # response=make_response(resfile)

    response.headers={"Access-Control-Allow-Origin":"*", 'Content-Type': "application/vnd.ms-excel"}
    response.headers['Content-Disposition'] = 'attachment; filename=FileName.xls'
    return response

#英文翻译，保存至englishdic
CORS(app,resources=r"/*")
@app.route('/fanyi', methods=['POST','GET'])
def fanyi():
    if request.method == 'POST':
        if request.data:
            data = json.loads(request.data)
        else:
            data=request.form
    else:
        data = request.args
    dicCollection = mydb['englishdic']

    query = {}
    query[data.get('from')]=data.get('result')
    query[data.get('to')]=data.get('q')
    result = dicCollection.find(query)
    print(result)

    #
    #
    response=Response()
    response.headers={"Access-Control-Allow-Origin":"*"}
    response.data=json.dumps(result)
    return response

CORS(app,resources=r"/*")
@app.route('/getfund', methods=['POST','GET'])
def getfund():
    if request.method == 'POST':
        if request.data:
            data = json.loads(request.data)
        else:
            data=request.form
    else:
        data = request.args
    page=Page(data.get("page")).page
    fund = myclient['stock_fund'].get_collection('fund')
    query = {}
    lis = fund.find(query,{"_id":0}).limit(page.get("pageSize")).skip(page.get("pageSize")*(page.get("current")-1))
    lis = list(lis)
    result = {
        'data': lis,
        'total': fund.count_documents(filter=query)
    }
    #
    #
    response=Response()
    response.headers={"Access-Control-Allow-Origin":"*"}
    response.data=json.dumps(result)
    return response
# schedule.every().wednesday.at("15:50").do(doWeek,wednesdayList)
# schedule.every().thursday.at("15:50").do(doWeek,thursdayList)
# schedule.every().day.at("20:00").do(doEvery)
# schedule.every().day.at("09:58").do(test)
if __name__ == '__main__':

    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
    kill_port('5000')
    time.sleep(3);
    threading.Thread(target=doSched).start()
    server = make_server('0.0.0.0', 5000, app)
    server.serve_forever()
    # pass
