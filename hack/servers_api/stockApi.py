# coding=utf-8
from hack.servers_api.serverApi import ServersApi
import datetime
from hack.include.list import findIndex, find_index
from hack.util import isNull
import hack.include.rili as rili
from hack.include.threadManage import ThreadManage
class StockApi(ServersApi):

    def __init__(self, app):
        ServersApi.__init__(self, app)
        self.threadManage = ThreadManage(1000)
        # 根据股票编号查询对应股票数据
        @self.register('/getstock', methods=['POST', 'GET'])
        def getstock(data):
            if data.get('code'):
                code = data.get('code')
                fund = self.myclient['dongfangcaifu'].get_collection(code)
                page = self.Page(data.get("page")).page
                sort = self.Sort({
                    'sort': data.get('sort'),
                    'order': data.get('order')
                }).sort
                query = {}
                lis = fund.find(query).sort(sort).limit(page.get("pageSize")).skip(
                    page.get("pageSize") * (page.get("current") - 1))
                lis = list(lis)
                for i in lis:
                    print(i['time'], i['time'].timestamp())
                    i['time'] = i['time'].timestamp() * 1000
                    i['_id'] = str(i['_id'])
                result = {
                    'data': lis,
                    'total': fund.count_documents(filter=query)
                }
                return result
            else:
                return '未查询到数据'

        # 获取股票名称列表
        @self.register('/getnames', methods=['POST', 'GET'])
        def getnames(data):
            fund = self.myclient['dongfangcaifu'].get_collection('names')
            page = self.Page(data.get("page")).page
            query = {}
            if data.get('search'):
                query['$or'] = [{ 'name': {'$regex': data.get('search')}}, { 'code': {'$regex': data.get('search')}}]
            lis = fund.find(query).limit(page.get("pageSize")).skip(
                page.get("pageSize") * (page.get("current") - 1))
            lis = list(lis)
            for i in lis:
                i['_id'] = str(i['_id'])
            result = {
                'data': lis,
                'total': fund.count_documents(filter=query)
            }
            return result

        # 更新汇总表数据
        @self.register('/updatestatistic', methods=['GET'])
        def update_statistic(data):
            limit = data.get('limit')
            now = datetime.datetime.now()
            try:
                self.updateToday(int(limit))
                return 'time:' + str(datetime.datetime.now() - now)
            except Exception as e:
                print(e,limit)
                return False


        # 获取汇总表数据
        @self.register('/stocklist', methods=['POST'])
        def stock_list(data):
            page = self.Page(data.get("page")).page
            sort = self.Sort({
                'sort': data.get('sort'),
                'order': data.get('order')
            }).sort
            query = {}
            if isNull(data.get("search")) is False:
                query['$or'] = [{ "f57": {'$regex': ".*" + data.get("search") + ".*"}}, { "f58": {'$regex': ".*" + data.get("search") + ".*"}}]
            totalDB = self.myclient['stock_statistic']['totalDB']
            lis = totalDB.find(query).sort(sort).limit(page.get("pageSize")).skip(
                page.get("pageSize") * (page.get("current") - 1))
            lis = list(lis)
            for i in lis:
                i['time'] = i['time'].timestamp() * 1000
                i['_id'] = str(i['_id'])
            result = {
                'data': lis or [],
                'total': totalDB.count_documents(filter=query)
            }
            return result

        # 最近连续下降次数最多的10个
        @self.register('/stock_stastic', methods=['POST'])
        def stock_stastic(data):
            stastic = Statistic(self.myclient)
            limit = data.get('limit') or 10
            day_limit = data.get('days') or 7
            return stastic.near_day(limit, day_limit, ['f43', 'f170'])

    # 执行欠缺表里欠缺的数据，更新到汇总表
    def do_short(self):
        shortDB = self.myclient['stock_statistic']['shortDB']
        shorts = shortDB.find()
        shorts = list(shorts)
        sort = [("time", -1)]
        def get_stock_short(i):
            current_time = shorts[i].get('time')
            next_time = datetime.datetime(year=current_time.year, month=current_time.month, day=current_time.day + 1)
            names = shorts[i].get('short') or []
            print(names)
            totalDB = self.myclient['stock_statistic']['totalDB']
            for name in names:
                stockDB = self.myclient['dongfangcaifu'].get_collection(name)
                data = stockDB.find({"time": {"$gte": current_time, "$lt": next_time}}).sort(sort).limit(1)
                data = list(data)
                if len(data) > 0:
                    data = data[0]
                else:
                    continue
                if data is not None:
                    totalDB.insert_one(data)
                    names.remove(name)

            shortDB.remove(shorts[i].get('_id'))
            shorts[i]['short'] = names
            shortDB.insert_one(shorts[i])
        for i in range(len(shorts)):
            self.threadManage.add(get_stock_short, (i,))


    # 更新股票汇总表
    def updateToday(self, limit=1):
        sort = [('time', -1)]
        now = datetime.datetime.now()
        # 汇总表：汇总据目前limit天的数据
        totalDB = self.myclient['stock_statistic']['totalDB']
        # 本次更新未汇入的表信息，执行次方法时可能有部分数据欠缺
        shortDB = self.myclient['stock_statistic']['shortDB']

        # 获取需要更新的日期
        def updateDays(limit_day):
            days = []
            now = datetime.datetime.now()
            shortDB = self.myclient['stock_statistic']['shortDB']
            shorts = shortDB.find().sort(sort)
            shorts = list(shorts)
            i = 0
            while i < limit_day:

                cur = datetime.datetime(year=now.year, month=now.month, day=now.day - i)
                if rili.isStockDeal(cur) is False:
                    limit_day += 1
                    i += 1
                    continue

                temp_time = datetime.datetime(year=cur.year, month=cur.month, day=cur.day + 1)
                print(cur, temp_time)
                exit = False
                for short in shorts:
                    short_time = short.get('time')
                    print(short_time)
                    if short_time >= cur and short_time < temp_time:
                        exit = True
                        break
                if exit is False:
                    days.append(cur)
                i += 1
            return days, limit_day

        days, limit_day = updateDays(limit)
        # 0点
        temp_time = datetime.datetime(year=now.year, month=now.month, day=now.day - limit_day + 1)
        # 删除超过需要汇总时间的数据
        shortDB.delete_many({
            "time": {"$lt": temp_time}
        })
        # 表明有数据过期，需对应删除汇总表数据
        totalDB.delete_many({
            "time": {"$lt": temp_time}
        })

        # 计算哪些天的数据需要新汇总
        shorts = shortDB.find().sort(sort)
        shorts = list(shorts)

        # 执行欠缺表中对应数据的汇总
        self.do_short()
        # 相等的话表明今天已经汇总过
        if len(shorts) == limit:
            return

        # 汇总
        def summary(days):
            print(days)
            sort = [("time", -1)]
            short_data = []
            for current_time in days:
                short_data.append({
                    "time": current_time,
                    "short": []
                })

            stocks = self.myclient['dongfangcaifu'].collection_names()
            def get_stock_limit(stock) :
                if findIndex([ 'names'],stock) > -1:
                    return
                stockDB = self.myclient['dongfangcaifu'].get_collection(stock)
                for i in range(len(days)):
                    current_time = days[i]

                    next_time = datetime.datetime(year=current_time.year, month=current_time.month, day=current_time.day + 1)
                    data = stockDB.find({"time": {"$gte": current_time, "$lt": next_time}}).sort(sort).limit(1)
                    data= list(data)
                    if len(data) > 0:
                        data = data[0]
                    else:
                        data = None
                    if data is None:
                        short_data[i].get('short').append(stock)
                    else:
                        if totalDB.find_one({'time': data.get('time')}) is None:
                            totalDB.insert_one(data)
            for stock in stocks:
                self.threadManage.add(get_stock_limit, (stock,))
            self.threadManage.run()
            self.threadManage.waiter()
            pass
        #     汇总完成，更新欠缺表
            for short in short_data:
                if short.get('_id') is None:
                    pass
                else:
                    shortDB.delete_one({"_id": short.get('_id')})
                shortDB.insert_one(short)
        summary(days)

from hack.util import mongodb_connect
class Statistic :
    def __init__(self, mongoClient=None):
        self.mongoClient = mongoClient or mongodb_connect()
        self.threadManage = ThreadManage(1000)
        self.statisticdb = self.mongoClient['stock_statistic']


    def n_diff(self, code, n=5, attribute="f57"):
        try:
            db = self.mongoClient['dongfangcaifu'].get_collection(code)

        except Exception as e:
            return e
    # 获取所有股票名称
    def getNames(self):
        fund = self.mongoClient['dongfangcaifu'].get_collection('names')
        return list(fund.find())

    # 最近连续下降次数最多的10个
    def near_day(self, limit=10, day_limit=10, attributes=["f43"]):
        results ={}
        for attribute in attributes:
            results[attribute] = []
        names = self.getNames()
        db = self.mongoClient['dongfangcaifu']
        sort = [("time", -1)]
        days = rili.stock_days(day_limit)

        for name in names:
            def computeDetail(name):
                code = name.get('code')
                next = None
                details = {}
                for attribute in attributes:
                    details[attribute] = {
                    "maxDiff": 0,
                    "min": 10000,
                    "max": 0,
                    #  连续下降数
                    'num': 0,
                    "code": code,
                    'name': name.get('name'),
                    'type': ''
                }
                for cur in days:
                    try:
                        next_time = rili.next_n_day(cur)
                        data = db[code].find({"time": {"$gte": cur, "$lt": next_time}}).sort(sort).limit(1)
                        data = list(data)
                        if len(data) > 0:
                            data = data.pop()
                        else:
                            continue
                        for attribute in attributes:
                            detail = details[attribute]
                            detail['min'] = min(detail['min'], data.get(attribute))
                            detail['max'] = max(detail['max'], data.get(attribute))
                            if next is not None:
                                if next.get(attribute) < data.get(attribute):
                                    detail['num'] += 1
                        next = data
                    except Exception as e:
                        print(e, data)
                        continue
                for attribute in attributes:
                    result = results[attribute]
                    detail = details[attribute]
                    detail['maxDiff'] = detail['max'] - detail['min']
                    if detail['max'] != 0:
                        detail['type'] = next.get('f127')
                        result.append(detail)
            self.threadManage.add(computeDetail, (name,))
        self.threadManage.run()
        self.threadManage.waiter()

        def sortfunc(data):
            return data.get('maxDiff')

        for attribute in attributes:
            result = results[attribute]
            result.sort(key=sortfunc, reverse=True)
            result = result[:limit]
        return results

    def calculate(self):
        db = self.statisticdb['calculate']
        names = self.getNames()
        for name in names:
            def calcu():
                data = {
                    "factor": ['f43', 'f135', 'f136', 'f137', 'f138', 'f139', 'f141', 'f142', 'f144']
                }
                pass



if __name__ == '__main__':
    now = datetime.datetime.now()
    cur = datetime.datetime(year=now.year, month=now.month, day=now.day - 1)
    da = Statistic()
    print('价值', '涨幅')
    print(da.near_day(10,30, ['f43', 'f170']))
