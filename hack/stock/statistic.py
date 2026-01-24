# coding=utf-8
from hack.util import mongodb_connect
from hack.include.threadManage import ThreadManage
from hack.util import build_date
import hack.include.rili as rili
from hack.include.list import findIndex, find_index
import datetime
from hack.journal import Journal
class Statistic:
    def __init__(self, mongoClient=None):
        self.mongoClient = mongoClient or mongodb_connect()
        self.threadManage = ThreadManage(1000)

        self.statisticdb = self.mongoClient['stock_statistic']
        self.journal = Journal(self)

    def n_diff(self, code, n=5, attribute="f57"):
        try:
            db = self.mongoClient['dongfangcaifu'].get_collection(code)

        except Exception as e:
            return e

        # 执行欠缺表里欠缺的数据，更新到汇总表
    def do_short(self):
        shortDB = self.mongoClient['stock_statistic']['shortDB']
        shorts = shortDB.find()
        shorts = list(shorts)
        sort = [("time", -1)]

        def get_stock_short(i):
            current_time = shorts[i].get('date')
            next_time = build_date(current_time, add_day=1)
            names = shorts[i].get('short') or []
            print(names)
            totalDB = self.mongoClient['stock_statistic']['totalDB']
            for name in names:
                stockDB = self.mongoClient['dongfangcaifu'].get_collection(name)
                data = stockDB.find({"date": {"$gte": current_time, "$lt": next_time}}).sort(sort).limit(1)
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
    def updateToday(self, limit=0):
        sort = [('time', -1)]
        now = datetime.datetime.now()
        # 汇总表：汇总据目前limit天的数据
        totalDB = self.mongoClient['stock_statistic']['totalDB']
        # 本次更新未汇入的表信息，执行次方法时可能有部分数据欠缺
        shortDB = self.mongoClient['stock_statistic']['shortDB']
        if limit == 0:
            limit = len(list(shortDB.find()))
        # 获取需要更新的日期
        def updateDays(limit_day):
            days = []
            now = datetime.datetime.now()
            shortDB = self.mongoClient['stock_statistic']['shortDB']
            shorts = shortDB.find().sort(sort)
            shorts = list(shorts)
            i = 0
            while i < limit_day:

                cur = build_date(now, add_day=-i)
                if rili.isStockDeal(cur) is False:
                    limit_day += 1
                    i += 1
                    continue

                temp_time = build_date(cur, add_day=1)
                print(cur, temp_time)
                exit = False
                for short in shorts:
                    short_time = short.get('date')
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
        temp_time = build_date(now, add_day=1 - limit_day)
        # 删除超过需要汇总时间的数据
        shortDB.delete_many({
            "date": {"$lt": temp_time}
        })
        # 表明有数据过期，需对应删除汇总表数据
        totalDB.delete_many({
            "date": {"$lt": temp_time}
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
            sort = [("date", -1)]
            short_data = []
            for current_time in days:
                short_data.append({
                    "date": current_time,
                    "short": []
                })

            stocks = self.mongoClient['dongfangcaifu'].collection_names()

            def get_stock_limit(stock):
                if findIndex(['names'], stock) > -1:
                    return
                stockDB = self.mongoClient['dongfangcaifu'].get_collection(stock)
                for i in range(len(days)):
                    current_time = days[i]

                    next_time = build_date(current_time, add_day=1)
                    data = stockDB.find({"date": {"$gte": current_time, "$lt": next_time}}).sort(sort).limit(1)
                    data = list(data)
                    if len(data) > 0:
                        data = data[0]
                    else:
                        data = None
                    if data is None:
                        short_data[i].get('short').append(stock)
                    else:
                        if totalDB.find_one({'date': data.get('date')}) is None:
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

    # 获取所有股票名称
    def getNames(self):
        fund = self.mongoClient['dongfangcaifu'].get_collection('names')
        return list(fund.find())

    # 最近连续下降次数最多的10个
    def near_day(self, limit=10, day_limit=10, attributes=["close"]):
        results = {}
        for attribute in attributes:
            results[attribute] = []
        names = self.getNames()
        db = self.mongoClient['dongfangcaifu']
        sort = [("date", -1)]
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
                        next_time = build_date(cur, add_day=1)
                        data = db[code].find({"date": {"$gte": cur, "$lt": next_time}}).sort(sort).limit(1)
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
                        self.journal.save(e)
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
            results[attribute] = result
        return results

    # 统计一天中最低点与最高点
    def day_calculate(self, code):
        db = self.mongoClient['dongfangcaifu'][code]
        start_date = datetime.datetime(year=2020, month=1, day=1)
        now = datetime.datetime.now()
        current_time = datetime.datetime(year=now.year, month=now.month, day=now.day)
        attibute = 'f43'
        day_db = self.mongoClient['statistic_day'][code]
        while current_time > start_date:
            if rili.isStockDeal(current_time):
                result = {
                    'min': 100000,
                    'max': 0,
                    'date': current_time
                }
                next_time = build_date(current_time, add_day=1)
                query = {"date": {"$gte": current_time, "$lt": next_time}}
                sort = [("date", -1)]
                if day_db.find_one(query) is not None:
                    break
                data = db.find(query).sort(sort)
                data = list(data)
                if len(data) > 0:
                    for da in data:
                        try:
                            if da.get(attibute) < result['min']:
                                result['min'] = da.get(attibute)
                                result['min_time'] = da.get('date')
                            if da.get(attibute) > result['max']:
                                result['max'] = da.get(attibute)
                                result['max_time'] = da.get('date')
                        except Exception as e:
                            self.journal.save(e)
                    day_db.insert_one(result)
            current_time = build_date(current_time, add_day=-1)

    # 统计一星期中最低点与最高点
    def week_calculate(self, code):
        db = self.mongoClient['dongfangcaifu'][code]
        start_date = datetime.datetime(year=2020, month=1, day=1)
        now = datetime.datetime.now()
        current_time = datetime.datetime.fromtimestamp(
            datetime.datetime(year=now.year, month=now.month, day=now.day).timestamp() - (
                        now.isoweekday() - 1) * 24 * 60 * 60)
        attibute = 'f43'
        week_db = self.mongoClient['statistic_week'][code]
        while current_time > start_date:
            result = {
                'min': 100000,
                'max': 0,
                'date': current_time
            }
            next_time = build_date(current_time, add_day=7)
            query = {"date": {"$gte": current_time, "$lt": next_time}}
            sort = [("date", -1)]
            if week_db.find_one(query) is not None:
                break
            data = db.find(query).sort(sort)
            data = list(data)
            if len(data) > 0:
                for da in data:
                    try:
                        if da.get(attibute) < result['min']:
                            result['min'] = da.get(attibute)
                            result['min_time'] = da.get('date')
                        if da.get(attibute) > result['max']:
                            result['max'] = da.get(attibute)
                            result['max_time'] = da.get('date')
                    except Exception as e:
                        self.journal.save(e)
                week_db.insert_one(result)
            current_time = build_date(current_time, add_day=-7)

    # 统计一月中最低点与最高点
    def month_calculate(self, code):
        db = self.mongoClient['dongfangcaifu'][code]
        start_date = datetime.datetime(year=2020, month=1, day=1)
        now = datetime.datetime.now()
        current_time = datetime.datetime(year=now.year, month=now.month, day=1)
        attibute = 'f43'
        month_db = self.mongoClient['statistic_month'][code]
        while current_time > start_date:
            result = {
                'min': 100000,
                'max': 0,
                'time': current_time
            }
            next_time = build_date(current_time, add_month=1)
            query = {"time": {"$gte": current_time, "$lt": next_time}}
            sort = [("time", -1)]
            if month_db.find_one(query) is not None:
                break
            data = db.find(query).sort(sort)
            data = list(data)
            if len(data) > 0:
                for da in data:
                    try:
                        if da.get(attibute) < result['min']:
                            result['min'] = da.get(attibute)
                            result['min_time'] = da.get('date')
                        if da.get(attibute) > result['max']:
                            result['max'] = da.get(attibute)
                            result['max_time'] = da.get('date')
                    except Exception as e:
                        self.journal.save(e)
                month_db.insert_one(result)
            current_time = build_date(current_time, add_month=-1)

    def calculate(self):
        names = self.getNames()
        for name in names:
            self.threadManage.add(self.day_calculate, (name['code'],))
            self.threadManage.add(self.month_calculate, (name['code'],))
            self.threadManage.add(self.week_calculate, (name['code'],))
        shortDB = self.mongoClient['stock_statistic']['shortDB']
        shorts = shortDB.find()
        shorts = list(shorts)
        self.threadManage.add(self.updateToday, (len(shorts),))
        self.threadManage.run()

if __name__ == '__main__':
    statistic = Statistic()
    print(type(statistic), 'gf')
    statistic.calculate()
