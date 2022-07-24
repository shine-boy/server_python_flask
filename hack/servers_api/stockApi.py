# coding=utf-8
from hack.servers_api.serverApi import ServersApi
import datetime
from hack.include.list import findIndex, find_index
from hack.util import isNull
import hack.include.rili as rili
class StockApi(ServersApi):

    def __init__(self, app):
        ServersApi.__init__(self, app)
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
                print(result)
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
            try:
                self.updateToday(int(limit))
                return True
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

    # 执行欠缺表里欠缺的数据，更新到汇总表
    def do_short(self):
        shortDB = self.myclient['stock_statistic']['shortDB']
        shorts = shortDB.find()
        shorts = list(shorts)
        sort = [("time", -1)]
        for i in range(len(shorts)):

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


    # 更新股票汇总表
    def updateToday(self, limit=1):
        sort = [('time', -1)]
        now = datetime.datetime.now()
        # 汇总表：汇总据目前limit天的数据
        totalDB = self.myclient['stock_statistic']['totalDB']
        # 本次更新未汇入的表信息，执行次方法时可能有部分数据欠缺
        shortDB = self.myclient['stock_statistic']['shortDB']
        # 0点
        temp_time = datetime.datetime(year=now.year, month=now.month, day=now.day - limit + 1)
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

        # 获取需要更新的日期
        def updateDays(limit_day):
            days = []
            now = datetime.datetime.now()
            shortDB = self.myclient['stock_statistic']['shortDB']
            shorts = shortDB.find().sort(sort)
            shorts = list(shorts)
            i = 0
            while i<limit_day:

                cur = datetime.datetime(year=now.year, month=now.month, day=now.day - i)
                if rili.isStockDeal(cur) is False:
                    limit_day+=1
                    i+=1
                    continue

                temp_time = datetime.datetime(year=cur.year, month=cur.month, day=cur.day + 1)
                exit = False
                for short in shorts:
                    short_time = short.get('time')
                    if short_time > cur and short_time < temp_time:
                        exit = True
                        break
                if exit is False:
                    days.append(cur)
                i+=1
            return days

        # 汇总
        def summary(days):
            sort = [("time", -1)]
            short_data = []
            for current_time in days:
                short_data.append({
                    "time": current_time,
                    "short": []
                })

            stocks = self.myclient['dongfangcaifu'].collection_names()
            for stock in stocks:
                if findIndex([ 'names'],stock) > -1:
                    continue
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
            pass
        #     汇总完成，更新欠缺表
            for short in short_data:
                if short.get('_id') is None:
                    pass
                else:
                    shortDB.delete_one({"_id": short.get('_id')})
                shortDB.insert_one(short)
        summary(updateDays(limit))

if __name__ == '__main__':
    now = datetime.datetime.now()
    cur = datetime.datetime(year=now.year, month=now.month, day=now.day - 1)
    print([][0])