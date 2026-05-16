# coding=utf-8
# from sklearn import svm
# from sklearn import datasets
import efinance as ef
from hack.util import mongodb_connect
import requests
import pickle
from datetime import datetime, timedelta
import time
import json
import csv
import pandas as pd


class getStockData():
    def __init__(self):
        pass
    # 从深圳交易所获取
    def fromSzce(self):
        params = {
            'SHOWTYPE': 'JSON',
            'CATALOGID': '1815_stock_snapshot',
            'TABKEY': 'tab1',
            'PAGENO': 1,
            'tab1PAGESIZE': 10,
            'txtBeginDate': '2024-07-25',
            'txtEndDate': '2024-07-29',
            'archiveDate': '2022-07-01',
            'random': '0.9307924288239493'
        }
        path = 'http://www.szse.cn/api/report/ShowReport/data'
        result = []
        map = {
        "jyrq": "交易日期",
        "zqdm": "证券号码",
        "zqjc": "证券简称",
        "qss": "开盘",
        "ks": "前收",
        "zg": "最高",
        "zd": "最低",
        "ss": "今收",
        "sdf": "涨跌幅",
        "cjgs": "成交量",
        "cjje": "成交金额",
        "syl1": "市赢率"
        }
        resultMap = {}
        keys = map.keys()
        def query():
            r1 = requests.get(url=path, params=params)  # 带参数的get请求
            # print(r1.request.url)
            text = r1.text
            params["PAGENO"] = 1
            res = json.loads(text)
            data = res[0].get('data')
            current = 2
            def loadData():
                for item in data:
                    temp = []
                    for key in keys:
                        temp.append(item[key])
                    if resultMap.get(item['zqdm']) is None:
                        resultMap[item['zqdm']] = []
                    resultMap.get(item['zqdm']).append(temp)
            loadData()
            pagecount = res[0].get('metadata').get('pagecount')
            while current<=pagecount:
                current = current+1
                params["PAGENO"] = current
                r1 = requests.get(url=path, params=params)  # 带参数的get请求
                # print(r1.request.url)
                text = r1.text
                res = json.loads(text)
                data = res[0].get('data')
                loadData()
        startData = datetime(2022, 7, 1)
        now = datetime.now()

        try:
            while startData<now:
                params["txtBeginDate"] = startData.strftime("%Y-%m-%d")
                startData = startData + timedelta(days=5)
                params["txtEndDate"] = startData.strftime("%Y-%m-%d")
                print(params["txtEndDate"])
                query()
                time.sleep(1000)
        except Exception as e:
            print(e)
        finally:
            filename = 'data'
            print(resultMap.get('000001'))
            ks = resultMap.keys()
            for k in ks:
                with open(filename+'//'+k+'.csv', 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows(resultMap[k])

def loadExcel(path):
    d = pd.read_csv('E:\\ChromeCoreDownloads\\FPT.csv')
    print(d)

def listToObj(data, columns, back):
    result =[]
    print(data)
    for item in data:
        print(item)
        temp = {}
        i=0
        for key in columns:
            temp[key] = item[i]
            i+=1
        result.append(temp)
    return result


class Stock():
    data = {}
    def __init__(self):
        self.myclient = mongodb_connect()

        self.mydb = self.myclient["dongfangcaifu"]
        self.etfDb = self.myclient["eftStock"]
        # 数据同步进度
        self.progress = 0
        pass
    def getCodes(self):
        names = self.mydb['names']
        return [doc['code'] for doc in names.find().sort('update', 1).sort('subscription', -1)]

    def getCodeKeysMap(self,codes=None):
        codes = self.getCodes() if codes is None else codes
        print(codes[0: 10])
        map = {}
        for code in codes:
            temp = self.getCodeBeginDate(code)
            if temp is not None:
                if map.get(temp) is None:
                    map[temp] = []
                map[temp].append(code)
        return map

    def addName(self, code, name):
        names = self.mydb['names']
        if names.find_one({
            "$or": [{'code': code}, {'name': name,}],

        }) is None:
            names.insert_one({
                'name': name,
                'code': code
            })

    def updateName(self, code, date = datetime.now()):
        names = self.mydb['names']
        query = {
            "$or": [{'code': code}],
        }
        item = names.find_one(query)

        if item is not None:

            item['update'] = datetime.now()
            names.update_one(query,{ "$set":{ 'update': date } } )



    def deleteStockData(self):
        dbs = self.mydb.list_collection_names()
        for name in dbs:
            if name != 'names':
                pass
                # self.mydb.drop_collection(name)

    def listToObj(self, data, columns):
        result = []
        for item in data:
            temp = {}
            i = 0
            for key in columns:
                temp[key] = item[i]
                i += 1
            if temp['close'] < 0:
                continue
            result.append(temp)

        return result

    def getCodeBeginDate(self, name, type='stock'):
        stockDb = self.mydb[name] if type == 'stock' else self.etfDb[name]

        data = [doc for doc in stockDb.find().sort('date', -1).limit(1)]
        beginData = '19000101'
        if len(data) > 0:
            data = data.pop()
        else:
            data = None
        if data is not None:
            now = datetime.now()
            lastDate = datetime.strptime(data['date'], '%Y-%m-%d')
            print(lastDate, '=====', data['date'].replace('-', ''))
            if (lastDate + timedelta(days=1)) > now:
                print('已经存在')
                return None
                pass
            if lastDate.weekday() == 4:
                if (lastDate + timedelta(days=3)) > now:
                    print('周日')
                    return None
                    pass
            beginData = data['date'].replace('-', '')

        return beginData

    def getStockData(self, code, type='stock'):
        beginData = self.getCodeBeginDate(code, type)
        if beginData is None:
            return None
        newData = self.data.get(beginData+'-'+code)
        if newData is not None:
            return newData
        # newData = ef.stock.get_quote_history(code, beg=beginData)
        return newData
    def updateStock(self, name, type='stock'):
        stockDb = self.mydb[name] if type == 'stock' else self.etfDb[name]
        # print(stockDb)

        data = [doc for doc in stockDb.find().sort('date', -1).limit(1)]

        if len(data) > 0:
            data = data.pop()
        else:
            data = None
        newData = self.getStockData(name, type)
        if newData is None:
            return
        # ['股票名称', '股票代码', '日期', '开盘', '收盘', '最高', '最低', '成交量', '成交额', '振幅', '涨跌幅',
        #        '涨跌额', '换手率']
        objLis = self.listToObj(newData.values.tolist(), ['name', 'code', 'date', 'open', 'close', 'high', 'low', 'volume', 'amount', 'volatility', 'Chg', 'change', 'TR' ])
        if objLis is None:
            return False
        if data is None:
            # print(newData)
            print(name, objLis[0].get('name'))
            self.addName(name, objLis[0].get('name'))
        i=0
        for obj in objLis:
            print(obj['date'])
            try:
                if data is None or data['date'] < obj['date']:
                    i+=1
                    print(obj['date'], i)
                    stockDb.insert_one(obj)
                    self.updateName(name, objLis[len(objLis) - 1]['date'])
            except Exception as e:
                print(e)
        return True

    def upDateAllStock(self,codes = None):
        codeKeyMap = self.getCodeKeysMap(codes)
        for beginData in codeKeyMap:
            print(beginData)

            for code in codeKeyMap[beginData]:
                print(code)
                try:
                    data = ef.stock.get_quote_history(code, beg=beginData)
                    print(data)
                    self.data[beginData + '-' + code] = data
                    self.updateStock(code)
                except Exception as e:
                    print('err', e)

        # names =  self.getCodes() if codes is None else codes
        # # print(names)
        # total = len(names)
        # if 0 != self.progress:
        #     return self.progress/total
        # for name in names:
        #     print(name)
        #     self.updateStock(name)
        #     self.progress+=1
        #     print(self.progress/total, '%')
        # self.progress = 0

    def getProgress(self):
        names = self.getCodes()
        total = len(names)
        return self.progress / total

    # 计算某只股票一周中最利于投资的一天
    def compute_max_good_day_code(self, code):
        dayUpMap = {
        }
        dayDownMap = {
        }
        stockDb = self.mydb[code]
        data = [doc for doc in stockDb.find().sort('date', -1)]
        for item in data:
            lastDate = datetime.strptime(item['date'], '%Y-%m-%d')
            week = lastDate.weekday() + 1
            if item['Chg'] > 0:
                if dayUpMap.get(week) is None:
                    dayUpMap[week] = 1
                else:
                    dayUpMap[week] += 1
            else:
                if dayDownMap.get(week) is None:
                    dayDownMap[week] = 1
                else:
                    dayDownMap[week] += 1
        return dayUpMap, dayDownMap

    # 计算一周中最利于投资的一天
    # 2024/11/8
    # up: ({3: 797922, 2: 837185, 4: 758340, 5: 783335, 1: 836412, 6: 26, 7: 35},
    # down: {4: 914892, 2: 830998, 1: 779190, 5: 862607, 3: 881442, 6: 90, 7: 22})
    # 周四降的最多，周二涨的概率更多
    def compute_max_good_day(self):
        codes = self.getCodes()
        dayUpMap = {
        }
        dayDownMap = {
        }
        def add_dic_num(a, b):
            c = {}
            c.update(b)
            for k in a.keys():
                if b.get(k) is None:
                    c[k] = a[k]
                else:
                    c[k] = a[k] + b[k]
            return c

        for code in codes:
            up, down = self.compute_max_good_day_code(code)
            dayUpMap = add_dic_num(dayUpMap, up)
            dayDownMap = add_dic_num(dayDownMap, down)
        return dayUpMap, dayDownMap

    def test(self):
        pass
        # clf = svm.SVC()
        # X, y = datasets.load_iris(return_X_y=True)
        # clf.fit(X, y)
        # s = pickle.dumps(clf)
        # clf2 = pickle.loads(s)
        # clf2.predict(X[0:1])

# import sys
# import os
# # linux下包导入失败
# path = os.path.abspath('./..')
# sys.path.append('/home/gitlab-runner/builds/NsGaLx8a/0/root/server_python_flask')  # 会追加到列表最尾部
# #
# sys.path.append(os.getcwd())  # 会追加到列表最尾部

if __name__ == '__main__':
    # loadExcel('')
    startData = datetime.now()
    print(type(startData))
    f = []
    f.extend([1,2])
    print(f)
    # myclient = mongodb_connect()
    # myclient.close()
    sto = Stock()
    # print(sto.updateStock())
    sto.upDateAllStock()
    # print(ef.stock.get_quote_history(['000066','000061']))
    # print(sto.getCodeKeysMap())
    # print(sto.getCodes())
    # sto.updateName('513130')
    sto.myclient.close()
    # stock_code = '600519'
    # data = ef.stock.get_quote_history(stock_code)
    # print(data.columns)

    # print(data.tail(5))


