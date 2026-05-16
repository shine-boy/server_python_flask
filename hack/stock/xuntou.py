
# coding:utf-8

import time, traceback, sys
from datetime import datetime, timedelta
import numpy as np
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from xtquant import xtconstant
import requests
from hack.util import mongodb_connect
globalData = {
    'startBuy': False
}
stockCache = {

}
def formateCode( code):
    if code.find('.') > -1:
        return  code
    if len(code) == 5:
        return code + '.HK'
    if code[0:3] in [ '920']:
        return  code + '.BJ'
    if code[0] in ['6', '5', '9']:
        return  code + '.SH'
    if code[0] in ['0', '3', '2']:
        return  code +'.SZ'
    if code[0] in ['1']:
        return code + '.SZ'

    return code

# 获取历史股票信息
def getHistoryData(codes, startDate):
    codes = [formateCode(code) for code in codes]
    #订阅最新行情
    # def callback_func(data):
    #     print('回调触发', data)
    xtdata.download_history_data2(stock_list= codes, period='1d',  start_time=startDate)
    # xtdata.subscribe_quote(code, period='1d', count=-1, callback= callback_func)
    data = xtdata.get_market_data_ex(field_list=[], stock_list= codes, period='1d', count=-1, start_time=startDate)
    result = {}
    for code in codes:
        result[code] = []
    # print(data)
    for key in data:
        # print(key)
        # print(data[key].head() )
        json_Obj = data[key].to_dict(orient='records')
        # print(json_Obj)
        result[key] = json_Obj
    # print(result)
    print('end')
    return  result
# code = '600000.SH'


class MyXtQuantTraderCallback(XtQuantTraderCallback):
    def on_disconnected(self):
        """
        连接断开
        :return:
        """
        print("connection lost, 交易接口断开，即将重连")
        xt_trader = None

    def on_stock_order(self, order):
        print(
            f'委托回报: 股票代码:{order.stock_code} 账号:{order.account_id}, 订单编号:{order.order_id} 柜台合同编号:{order.order_sysid} \
            委托状态:{order.order_status} 委托数量:{order.order_volume} 已成数量：{order.traded_volume}')
        print()
        global globalData
        if order.order_status == 54:
            # 已撤
            globalData['startBuy'] = True


    def on_stock_trade(self, trade):
        print(
            f'成交回报: 股票代码:{trade.stock_code} 账号:{trade.account_id}, 订单编号:{trade.order_id} 柜台合同编号:{trade.order_sysid} \
            成交编号:{trade.traded_id} 成交数量:{trade.traded_volume} 委托数量:{trade.direction} {datetime.fromtimestamp(trade.order_time)}')
        time.sleep(2)
        fetchPost('/drawServer/transaction', trade)
        global stockCache, globalData
        globalData['startBuy'] = True
        if trade.strategy_name == 'sell':
            stockBuySell.codes.append(trade.stock_code)
        if trade.strategy_name == 'buy':
            data = stockCache.get(trade.stock_code)
            if data is not None:
                data.buyNum = trade.traded_volume

    def on_order_error(self, order_error):
        print(
            f"报单失败： 订单编号：{order_error.order_id} 下单失败具体信息:{order_error.error_msg} 委托备注:{order_error.order_remark}")
        if order_error.strategy_name == 'buy':
            stockBuySell.codes.append(order_error.stock_code)

    def on_cancel_error(self, cancel_error):
        print(
            f"撤单失败: 订单编号：{cancel_error.order_id} 失败具体信息:{cancel_error.error_msg} 市场：{cancel_error.market}")

    def on_order_stock_async_response(self, response):
        print(f"异步下单的请求序号:{response.seq}, 订单编号：{response.order_id} ")

    def on_account_status(self, status):
        print(f"账号状态发生变化， 账号:{status.account_id} 最新状态：{status.status}")


def getCodes():
    data = fetchPost('/drawServer/getSellCodes', {})
    codes = []
    if data is not None:
        for code in data['data']:
            code_ = formateCode(code)
            if code_ in codes:
                continue
            codes.append(code_)
    return  codes

def getLastStockData(codes):
    codes = [formateCode(code) for code in codes]
    full_tick = xtdata.get_full_tick(codes)
    resultData = {}
    for code in codes:
        code_ = code.split('.')[0]

        item = full_tick.get(code)
        if item is None:
            print('没找到', code)
            continue
        resultData.setdefault(code_, item)
    return resultData


rootPath = 'http://localhost:3001'

def fetchPost(url, params):
    headers = {
        "Content-Type": "application/json",
        "Connection": "close"
    }
    response = requests.post(rootPath+url, json=params, headers=headers)
    if response.status_code == 200:
          # 假设返回的是JSON格式的数据
        return response.json()
    else:
        print("请求失败，状态码：", response.status_code)
    return None

class CacheStock(object):
    buyItem = None
    sellItem = None
    code = None
    open_price = None
    poor = None
    buyPrice = None
    buyNum = None
    def __init__(self, code):
        self.code = code
        pass
    def getLastData(self):
        # 取全推数据
        full_tick = xtdata.get_full_tick([self.code])
        # print('全推数据 日线最新值', full_tick[self.code])

        if self.open_price is None:
            self.open_price = self.getOpen(full_tick[self.code])
        if self.poor is None:
            self.computeMaxDigits(full_tick[self.code])
        return full_tick[self.code]

    def getOpen(self, full_tick):
        lastDate = datetime.fromtimestamp(full_tick['time'] / 1000)
        now = datetime.now()
        open_price = full_tick['lastPrice']

        if now.strftime("%Y-%m-%d") == lastDate.strftime("%Y-%m-%d"):
            open_price = full_tick['open'] if full_tick['open'] else full_tick['lastPrice']
        return  min(open_price, full_tick['lastClose']*1.01)

    def computeRate(self, value):
        return abs((value-self.open_price)/ self.open_price)

     # 计算含有最大小数的值
    def computeMaxDigits(self, data):
        max = 0
        for value in [data['open'], data['lastPrice'], data['lastClose']]:
            if str(value).find('.')==-1:
                continue
            temp = len(str(value).split('.')[1])
            if temp > max:
                max = temp
        self.poor = pow(10, -max) * 1


    def getBuyItem(self, info, hasInfo):
        # print('getBuyItemCode', self.code)
        now = datetime.now()
        self.getLastData()
        available_cash = info['available_cash']
        self.buyItem = fetchPost('/drawServer/buyItem', {
            'code': self.code.split('.')[0], 'date': now.strftime("%Y-%m-%d"), 'allValue': available_cash, 'hasInfo': hasInfo,
            'startValue': self.open_price, 'has': hasInfo.get(self.code).get('has') if hasInfo.get(self.code) else 0
        })
        if self.buyItem is None:
            stockBuySell.codes.append(self.code)
            return None
        if self.buyItem.get('data') is None:
            return None
        full_tick = self.getLastData()
        data = self.buyItem['data']
       # if full_tick['lastPrice'] > self.open_price:
         #   return None
        if data.get('buyValue') is None:
            return  None
        print(self.code, data['buyValue'], full_tick['lastPrice'])
        if full_tick['lastPrice'] <= (data['buyValue']):
            return self.buyItem
        stockBuySell.codes.append(self.code)
        return None

    def getSellItem(self, info, hasInfo):
        now = datetime.now()
        available_cash = info['available_cash']
        self.getLastData()
        self.sellItem = fetchPost('/drawServer/sellItem', {
            'code': self.code.split('.')[0], 'date': now.strftime("%Y-%m-%d"), 'allValue': available_cash,'hasInfo': hasInfo,
            'startValue': self.open_price, 'has': hasInfo.get(self.code).get('canSell') if hasInfo.get(self.code) else 0
        })
        if self.sellItem is None or self.sellItem.get('data') is None:
            self.sellItem=None
            return None
        full_tick = self.getLastData()
        data = self.sellItem['data']
        if data.get('sellValue') is None:
            return None

        # 连续上涨则不着急卖出
        # if self.buyItem:
        #     buyData = self.buyItem['data']
        #     if buyData.get('predictValue') < buyData.get('predictValue2') and self.buyNum is None:
        #         return  None
        if full_tick['lastPrice'] >= (data['sellValue']):
                return self.sellItem
        return None

    def cancelSell_Buy(self):
        if self.buyItem is None:
            return None
        full_tick = self.getLastData()
        data = self.buyItem['data']
        if full_tick['lastPrice'] >= (data['buyValue'] + self.poor * 5):
            return True
        return False


class StockBuySell:
    xt_trader = None
    xt_acc = None
    codeMap ={}
    codes = []
    path = r'D:\国金证券QMT交易端\userdata_mini'
    def __init__(self):
        # getHistoryData([code])
        # 创建资金账号为 800068 的证券账号对象 股票账号为STOCK 信用CREDIT 期货FUTURE
        xt_acc = StockAccount('8885093902')
        self.xt_acc = xt_acc
        xt_trader = self.get_xttrader()

        if not xt_trader:
            raise Exception('交易接口连接失败')
        print('交易接口连接成功， 策略开始')

        self.xt_trader = xt_trader
    # 获取最新一天日线信息
    def create_trader(self,session_id):
        trader = XtQuantTrader(self.path, session_id, callback=MyXtQuantTraderCallback())
        trader.start()
        connect_result = trader.connect()
        trader.subscribe(self.xt_acc)
        return trader if connect_result == 0 else None

    def try_connect(self):
        session_id_range = [i for i in range(100, 120)]

        import random
        random.shuffle(session_id_range)

        # 遍历尝试session_id列表尝试连接
        for session_id in session_id_range:
            trader = self.create_trader( session_id)
            if trader:
                print('连接成功，session_id:{}', session_id)
                return trader
            else:
                print('连接失败，session_id:{}，继续尝试下一个id', session_id)
                continue

        print('所有id都尝试后仍失败，放弃连接')
        return None

    def get_xttrader(self):
        if self.xt_trader is None:
            self.xt_trader = self.try_connect()
        return self.xt_trader

    def getLastData(self,code):
        # 取全推数据
        full_tick = xtdata.get_full_tick([code])
        # print('全推数据 日线最新值', full_tick[code])
        return full_tick[code]

    def getInfo(self):
        # 取账号信息
        account_info = self.xt_trader.query_stock_asset(self.xt_acc)
        result = {
            'available_cash': account_info.cash,  # 取可用资金
        }
        hasInfo = {}
        # 查账号持仓
        positions = self.xt_trader.query_stock_positions(self.xt_acc)
        # 取各品种 总持仓 可用持仓
        for i in positions:
            if hasInfo.get(i.stock_code) is None:
                hasInfo[i.stock_code] = {}
            hasInfo[i.stock_code]['has'] = i.volume
            hasInfo[i.stock_code]['canSell'] = i.can_use_volume
            hasInfo[i.stock_code]['value'] = i.market_value
            hasInfo[i.stock_code]['avgPrice'] = i.avg_price


        # print('账户信息',result, hasInfo, len(hasInfo))
        return result,hasInfo

    def hasBuyDoing(self, stock_code):
        # 委托信息查询
        orders = self.xt_trader.query_stock_orders(self.xt_acc, False)

        for order in orders:
            if stock_code == order.stock_code and order.strategy_name == 'buy' and order.order_status == 50:
                return  True
            # print(order.stock_code, order.order_type, order.order_volume, order.order_status, order.strategy_name)
        return  False

    def cancelSell_Buy(self):
        # 委托信息查询
        orders = self.xt_trader.query_stock_orders(self.xt_acc, False)

        for order in orders:
            if order.strategy_name == 'buy' and order.order_status == 50:
                stockData = self.getStockData(order.stock_code)
                if stockData.cancelSell_Buy():
                    flag = self.xt_trader.cancel_order_stock(self.xt_acc, order.order_id)
                    print('撤单', flag)
                    if flag == 0:
                        stockBuySell.codes.append(order.stock_code)


            if order.strategy_name == 'sell' and order.order_status == 50:
                return True
        return False

    def getOpen(self, code):
        full_tick = self.getLastData(code)
        lastDate = datetime.fromtimestamp(full_tick['time'] / 1000)
        now = datetime.now()
        if now.strftime("%Y-%m-%d") == lastDate.strftime("%Y-%m-%d"):
            return full_tick['open'] if full_tick['open'] else full_tick['lastPrice']
        return  full_tick['lastPrice']


    def startBuy(self):
        self.get_xttrader()
        global globalData
        info, hasInfo = self.getInfo()
        data = fetchPost('/drawServer/getSellCodes', {})
        print(data)
        # 添加已持有的股票
        # codes = {i: 1 for i in hasInfo.keys()}
        # self.codes = [i for i in codes.keys()]
        if data is not None:
            for code in data['data']:
                code_ = formateCode(code)
                if code_ in self.codes:
                    continue
                self.codes.append(code_)
        for i in hasInfo:
            item = hasInfo[i]
            if i in self.codes:
                continue
            self.codes.append(i)

        globalData['startBuy'] = True
        # self.buyNext()

    def buyNext(self):

        global globalData
        if len(self.codes) == 0:
            return
        info, hasInfo = self.getInfo()
        available_cash = info['available_cash']
        if available_cash < 16000:
            globalData['startBuy'] = False
            return

        for i in range(len(self.codes)):
            try:
                self.buy(self.codes.pop(0))

            except Exception as e:
                print(e)

    def getStockData(self, code):
        stockData = None
        global stockCache
        if stockCache.get(code) is None:
            stockData = CacheStock(code)
            stockCache[code] = stockData
        else:
            stockData = stockCache.get(code)
        return stockData
    # 是递增
    def isInc(self, full_tick, type):

        # 买5
        bidVol = full_tick.get('bidVol') or []
        # 卖5
        askVol = full_tick.get('askVol') or []
        arr = bidVol if type == 'buy' else askVol
        if arr is None or len(arr) == 0:
            return False
        pre =arr[0]
        for i in arr[1:-1]:
            if pre > i:
                return False
        if type == 'sell':
            return bidVol[0] > bidVol[1] + bidVol[2] + bidVol[3]
        if type == 'buy':
            return askVol[0] > askVol[1] + askVol[2] + askVol[3]
        return True
    def buy(self, code):
        if self.hasBuyDoing(code):
            return
        stockData = self.getStockData(code)

        info, hasInfo = self.getInfo()
        if hasInfo.get(code) is not None and hasInfo[code]['has'] != hasInfo[code]['canSell']:
            return
        buyItem = stockData.getBuyItem(info, hasInfo)

        if buyItem:
            data = buyItem['data']
            print(code, 'buy',buyItem)
            full_tick = stockData.getLastData()
            if self.isInc(full_tick, 'buy'):
                self.codes.insert(0, code)
                return

            buyValue = min(data['buyValue'], full_tick['lastPrice'])
            if data['buyNum'] > 0:
                async_seq = self.xt_trader.order_stock_async(self.xt_acc, code, xtconstant.STOCK_BUY, data['buyNum'], xtconstant.FIX_PRICE,
                                                buyValue,
                                                'buy', code)
            else:
                self.codes.append(code)


    def doSell(self):
        # self.sell()
        info, hasInfo = self.getInfo()
        for i in hasInfo:
            item = hasInfo[i]
            if item.get('canSell') > 0:
                try:
                    self.sell(i, info, hasInfo)
                except Exception as e:
                    print(e)
        available_cash = info['available_cash']
        if available_cash > 16000:
            globalData['startBuy'] = True
        pass
    def sell(self, code, info, hasInfo):

        stockData = self.getStockData(code)
        sellItem = stockData.getSellItem(info, hasInfo)

        if sellItem:
            data = sellItem['data']
            full_tick = stockData.getLastData()
            if self.isInc(full_tick, 'sell'):
                self.sell(code, info, hasInfo)
                return
            print(code, 'sell', sellItem)
            sellValue = max(data['sellValue'], full_tick['lastPrice'])
            if sellItem.get('immediately') is True:
                # 立刻卖出
               sellValue = full_tick['lastPrice']
            if data['sellNum'] > 0:
                async_seq = self.xt_trader.order_stock_async(self.xt_acc, code, xtconstant.STOCK_SELL, data['sellNum'],
                                                        xtconstant.FIX_PRICE,
                                                        sellValue,
                                                        'sell', code)

    # 是交易日
    def isTranding(self, code):
        now = datetime.now()
        dataItem = self.getLastData(formateCode(code))
        if dataItem is None:
            return False
        if now.strftime('%Y%m%d') == dataItem['timetag'].split(' ')[0]:
            return True
        return False

    def cancel_order(self, code, info, order):
        orderItem = order.get(code)
        if orderItem is not None:
            return


    def getOrderInfo(self):
        orders = self.xt_trader.query_stock_orders(self.xt_acc, cancelable_only=False)
        info = {}
        # 取各品种 总持仓 可用持仓
        for i in orders:
            info[i.stock_code] = i
        return info

    def doSome(self):
        info, hasInfo = self.getInfo()
        order = self.getOrderInfo()
        for code in self.codes:
            self.cancel_order(code, info, order)


def test():
    # d = fetchPost('/drawServer/sellItem', {
    #     'code': '002594', 'date': now.strftime("%Y-%m-%d"), 'allValue': 50000,
    #     'startValue': 103.51, 'has':  200
    # })
    # print(d)
    # getLastStockData()
    # getHistoryData([formateCode('002428')])
    pass
    # globalData['startBuy'] = False
stockBuySell = None
def runXunTou():
    print('==================')
    now = datetime.now()
    print(getHistoryData(['300379.SZ'], ''))
    global stockBuySell
    stockBuySell = StockBuySell()
    # stockBuySell.startBuy()
    # stockBuySell.buyNext()
    # stockBuySell.buy(formateCode('002475'))
    # info, hasInfo = stockBuySell.getInfo()
    # print(hasInfo)
    # stockBuySell.sell(formateCode('001280'), info, hasInfo)
    # stockBuySell.buy(formateCode('001379'))
    # globalData['stockBuySell'] = stockBuySell
    # stockBuySell.hasBuyDoing('')
    # stockBuySell.doSell()

    startStr = ' 09:30:00'
    startCodeStr = ' 09:33:00'
    endStr = ' 15:00:00'
    test()
    startDate = datetime.fromisoformat(now.strftime('%Y-%m-%d') + startStr)
    endDate = datetime.fromisoformat(now.strftime('%Y-%m-%d') + endStr)
    if startDate < now < endDate:
        if stockBuySell.isTranding('000816'):
            stockBuySell.startBuy()
    while True:
        now = datetime.now()
        startDate = datetime.fromisoformat(now.strftime('%Y-%m-%d') + startStr)
        startCodeDate = datetime.fromisoformat(now.strftime('%Y-%m-%d') + startCodeStr)
        endDate = datetime.fromisoformat(now.strftime('%Y-%m-%d') + endStr)
        if datetime.fromisoformat(now.strftime('%Y-%m-%d') + ' 11:30:00') < now < datetime.fromisoformat(
                now.strftime('%Y-%m-%d') + ' 13:00:00'):
            continue
        if startDate < now < startCodeDate and len(stockBuySell.codes) == 0:
            if stockBuySell.isTranding('000816'):
                stockBuySell.startBuy()
        if endDate < now or now < startDate or now.isoweekday() in [6, 7]:
            stockBuySell.codes = []
            globalData['startBuy'] = False
            stockCache = {}
            pass
            continue
        if startDate < now < endDate:
            if globalData['startBuy']:
                if len(stockBuySell.codes) > 0:
                    stockBuySell.buyNext()
                stockBuySell.cancelSell_Buy()
                print('=============', datetime.now().timestamp() - now.timestamp())
            print(stockBuySell.codes)
            print('doSell', now)
            stockBuySell.doSell()

        if (1 - (datetime.now().timestamp() - now.timestamp())) > 0:
            time.sleep(1 - (datetime.now().timestamp() - now.timestamp()))
    # 死循环 阻塞主线程退r

    # xtdata.run()



# coding:gbk


class StockData:
    def __init__(self):
        self.myclient = mongodb_connect()
        self.mydb = self.myclient["dongfangcaifu"]
        pass
    def isDirtyData(self, item):
        high = item.get('high')
        open = item.get('open')
        low = item.get('low')
        close = item.get('close')
        if close is None or open is None or low is None or high is None:
            return True
        if np.isnan(close) or np.isnan(open) or np.isnan(low) or np.isnan(high):
            return True
        if close == open == low == high:
            return True
        return False

    def getStockData(self, code_list = ["000001.SZ", "600519.SH"], start_date = '', end_date = "", period = "1d"):
        # start_date = '20231001'  # 格式"YYYYMMDD"，开始下载的日期，date = ""时全量下载
        # end_date = ""
        # period = "1d"
        code_list = [formateCode(code) for code in code_list]
        need_download = 0   # 取数据是空值时，将need_download赋值为1，确保正确下载了历史数据
        if need_download:  # 判断要不要下载数据, gmd系列函数都是从本地读取历史数据,从服务器订阅获取最新数据
            self.my_download(code_list, period, start_date, end_date)

        ############ 仅获取历史行情 #####################
        # subscribe = False  # 设置订阅参数，使gmd_ex仅返回本地数据
        # count = -1  # 设置count参数，使gmd_ex返回全部数据
        # data1 = C.get_market_data_ex([], code_list, period=period, start_time=start_date, end_time=end_date,
        #                              subscribe=subscribe)
        #
        # ############ 仅获取最新行情 #####################
        # subscribe = True  # 设置订阅参数，使gmd_ex仅返回最新行情
        # count = 1  # 设置count参数，使gmd_ex仅返回最新行情数据
        # data2 = C.get_market_data_ex([], code_list, period=period, start_time=start_date, end_time=end_date,
        #                              subscribe=subscribe, count=1)  # count 设置为1，使返回值只包含最新行情

        ############ 获取历史行情+最新行情 #####################
        subscribe = True  # 设置订阅参数，使gmd_ex仅返回最新行情
        count = -1  # 设置count参数，使gmd_ex返回全部数据
        data3 = xtdata.get_market_data_ex([], code_list, period=period, start_time=start_date, end_time=end_date,
                                      count=-1)  # count 设置为-1，使返回值包含最新行情和历史行情

        # print(data1[code_list[0]].tail())  # 行情数据查看
        # print(data2[code_list[0]].tail())
        result = {}
        for code in code_list:
            result[code] = self.handelData(data3[code].to_dict(orient='records'))

        return result

    def updateStockData(self, item):
        data = {
            'name': item.get('name'), 'code': item['code'],
            'date': item['time'],
            'open': item['open'],
            'close': item['close'],
            'high': item['high'],
            'low': item['low'],
            'volume': item['volume'],
            'amount': item['amount'],
            }
        print(data)
        fetchPost('/toShare/updateStockData', {
            'item': data
        })
    def updateStockDatas(self):

        needUpdateNames = self.getNeedUpdateNames()

        needUpdateCode = []
        for name in needUpdateNames:
            needUpdateCode.append(name.get('ts_code') or formateCode(name.get('code')))
        print('needUpdateCode', len(needUpdateCode))
        return
        datas = self.getStockData(code_list=needUpdateCode)
        for name in needUpdateNames:
            ts_code = name.get('ts_code') if name.get('ts_code') else formateCode(name.get('code'))
            print(ts_code)
            data = datas[ts_code]

            for item in data:
                item.setdefault('code', name.get('code'))
                item.setdefault('name', name.get('name'))
                self.updateStockData(item)


    # 清洗数据
    def handelData(self, data):
        result = []
        for item in data:
            if self.isDirtyData(item):
                continue
            result.append(item)
        return result
    def getSectorList(self):
        sector_list = xtdata.get_sector_list()
        sectors = []
        for sector in sector_list:
            if 'ETF' in sector:
                sectors.append({'sector': sector, 'type': 'etf'})
            elif '香港' in sector:
                sectors.append({'sector': sector, 'type': 'hStock'})
        codeItems = []
        for sectorItem in sectors:
            sector = sectorItem['sector']

            codeList = xtdata.get_stock_list_in_sector(sector)
            codeItems.extend(
                [{'sector': sector, 'type': sectorItem['type'], 'ts_code': ts_code} for ts_code in codeList])
        return codeItems
    def updateStockNames(self):
        codeItems = self.getSectorList()
        for codeItem in codeItems:
            self.updateName(codeItem.get('ts_code').split('.')[0], codeItem)
        # print(sectors)
    def updateName(self, code, data = {}, deleteData = {}):
        print(code, data)
        data['code'] = code
        nameCollection = self.mydb['names']
        nameCollection.update_one(
        { 'code': code },
        {
          '$set': data,
          '$unset': deleteData,
        },
        True
        )

    def my_download(self,stock_list, period, start_date='', end_date=''):
        '''
        用于显示下载进度
        '''
        if "d" in period:
            period = "1d"
        elif "m" in period:
            if int(period[0]) < 5:
                period = "1m"
            else:
                period = "5m"
        elif "tick" == period:
            pass
        else:
            raise KeyboardInterrupt("周期传入错误")

        n = 1
        num = len(stock_list)
        for i in stock_list:
            print(f"当前正在下载{n}/{num}")
            xtdata.download_history_data(i, period, start_date, end_date)
            n += 1
        print("下载任务结束")
    def getNeedUpdateNames(self):
        namesCollection = self.mydb['names']
        names = namesCollection.find()
        needUpdateNames = []
        for name in names:
            if name.get('type') == 'hStock' or name.get('type') == 'etf':
                if name.get('update') != '2026-05-15':
                     needUpdateNames.append(name)

        return needUpdateNames

    def hasNameData(self):
        nameCollection = self.mydb['names']
        collection_names = self.mydb.list_collection_names()
        print(collection_names)
        print(len(collection_names))
        nameItems = nameCollection.find()
        codeItems = self.getSectorList()
        print(codeItems)
        codes = [codeItem['ts_code'] for codeItem in codeItems]
        print(codes)
        for name in nameItems:
            if name['code'] not in collection_names:
                if name['ts_code'] not in codes:
                    print(name)


if __name__ == '__main__':
# 迅投研 xtquant 示例
    stockData = StockData()
    stockData.updateStockDatas()
    # print([0,1][-1])
    # print(stockData.getNeedUpdateNames())
