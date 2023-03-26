# coding=utf-8
from hack.servers_api.serverApi import ServersApi
import datetime
from hack.util import isNull
from hack.include.threadManage import threadManage
from hack.stock import Statistic
# from hack.tensflow.soft import StockSoft
class StockApi(ServersApi):

    def __init__(self, app):
        ServersApi.__init__(self, app)
        self.threadManage = threadManage
        self.statistic = Statistic(self.myclient)
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
                if data.get('startTime'):
                    query['time'] = {"$gt": data.get('startTime')}
                if page.get('current') == -1:
                    lis = fund.find(query).sort(sort)
                else:
                    lis = fund.find(query).sort(sort).limit(page.get("pageSize")).skip(
                        page.get("pageSize") * (page.get("current") - 1))
                lis = list(lis)
                for i in lis:
                    i['time'] = i['time'].timestamp() * 1000
                    i['_id'] = str(i['_id'])
                result = {
                    'data': lis,
                    'total': fund.count_documents(filter=query)
                }
                return result
            else:
                return '未查询到数据'

        # 根据股票编号预测-+对应股票数据
        @self.register('/getcaculatestock', methods=['POST', 'GET'])
        def getcaculatestock(data):
            if data.get('code'):
                code = data.get('code')
                fund = self.myclient['dongfangcaifu'].get_collection(code)
                sort = self.Sort().sort
                query = {}
                end = fund.find(query).sort(sort).limit(1)
                end = list(end).pop()
                start_time = end['time'].timestamp() + 3*60
                if data.get('startTime'):
                    start_time = data.get('startTime')
                now = datetime.datetime.now()
                end_time = datetime.datetime(year= now.year, month=now.month, day=now.day, hour=15).timestamp()
                lis = []
                while start_time < end_time:
                    temp = end.copy()
                    start_time += 3*60
                    yu = start_time%24*60*60
                    if yu < 9.5*60*60 or (yu > 11.5*60*60 and yu < 13*60*60) or yu > 15*30*30:
                        continue
                    temp['target_diff_time'] = 3*60
                    temp['time'] = datetime.datetime.fromtimestamp(start_time)
                    lis.append(temp)
                # stockSoft = StockSoft()
                # pres = stockSoft.predict(code, lis)
                for i in range(list(lis)):
                    lis[i]['time'] = lis[i]['time'].timestamp() * 1000
                    lis[i]['_id'] = str(lis[i]['_id'])
                    # lis[i]['f43'] = pres[i]
                result = {
                    'data': lis,
                    'total': len(lis)
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
                self.statistic.updateToday(int(limit))
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
            limit = data.get('limit') or 10
            day_limit = data.get('days') or 7
            return self.statistic.near_day(limit, day_limit, ['f43', 'f170'])


if __name__ == '__main__':
    print(12%10)
    # now = datetime.datetime.now()
    # cur = datetime.datetime(year=now.year, month=now.month, day=now.day - 1)
    #
    # print('价值', '涨幅')
    # print(datetime.datetime(year=now.year, month=12, day=1))

