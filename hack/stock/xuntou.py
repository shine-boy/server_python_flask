
# coding:utf-8

import time, traceback, sys
from datetime import datetime, timedelta
from xtquant import xtdata
from xtquant.xttrader import XtQuantTrader, XtQuantTraderCallback
from xtquant.xttype import StockAccount
from xtquant import xtconstant
import requests

globalData = {
    'startBuy': False
}
stockCache = {

}

# 获取历史股票信息
def getHistoryData(codes):
    #订阅最新行情
    # def callback_func(data):
    #     print('回调触发', data)
    # xtdata.subscribe_quote(code, period='1d', count=-1, callback= callback_func)
    data = xtdata.get_market_data([], codes, period='1d', count=1)
    # print('一次性取数据', data)
    result = {}
    for code in codes:
        result[code] = []
    # print(data)
    for key in data:
        i = 0
        for column in data[key].columns:
            for code in codes:
                if i>= len(result[code]):
                    result[code].append({'date': column })
                result[code][i][key] = data[key].loc[code, str(column)]
                # print(data[key].loc[code, str(column)])
            pass
            i += 1
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
        if order.order_status == 54:
            # 已撤
            globalData['startBuy'] = True


    def on_stock_trade(self, trade):
        print(
            f'成交回报: 股票代码:{trade.stock_code} 账号:{trade.account_id}, 订单编号:{trade.order_id} 柜台合同编号:{trade.order_sysid} \
            成交编号:{trade.traded_id} 成交数量:{trade.traded_volume} 委托数量:{trade.direction} {datetime.fromtimestamp(trade.order_time)}')
        if trade.strategy_name == 'sell':
            globalData['startBuy'] = True
            stockBuySell.codes.append(trade.stock_code)

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



rootPath = 'http://localhost:3001'

def fetchPost(url, params):
    headers = {
        "Content-Type": "application/json",
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
        print('getBuyItemCode', self.code)
        if self.buyItem is None:
            now = datetime.now()
            self.getLastData()
            available_cash = info['available_cash']
            self.buyItem = fetchPost('/drawServer/buyItem', {
                'code': self.code.split('.')[0], 'date': now.strftime("%Y-%m-%d"), 'allValue': available_cash,
                'startValue': self.open_price, 'has': hasInfo.get(self.code).get('has') if hasInfo.get(self.code) else 0
            })
        if self.buyItem is None or self.buyItem.get('data') is None:
            self.buyItem = None
            return None
        full_tick = self.getLastData()
        data = self.buyItem['data']
        if full_tick['lastPrice'] > self.open_price:
            stockBuySell.codes.append(self.code)
            return None
        if data.get('buyValue') is None:
            return  None
        if full_tick['lastPrice'] <= (data['buyValue'] + self.poor):
                return self.buyItem
        stockBuySell.codes.append(self.code)
        return None

    def getSellItem(self, info, hasInfo):
        if self.sellItem is None:
            now = datetime.now()
            available_cash = info['available_cash']
            self.getLastData()
            self.sellItem = fetchPost('/drawServer/sellItem', {
                'code': self.code.split('.')[0], 'date': now.strftime("%Y-%m-%d"), 'allValue': available_cash,
                'startValue': self.open_price, 'has': hasInfo.get(self.code).get('has') if hasInfo.get(self.code) else 0
            })
        if self.sellItem is None or self.sellItem.get('data') is None:
            self.sellItem=None
            return None
        full_tick = self.getLastData()
        data = self.sellItem['data']
        if data.get('sellValue') is None:
            return None
        if full_tick['lastPrice'] >= (data['sellValue'] - self.poor):
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
        print('全推数据 日线最新值', full_tick[code])
        return full_tick[code]

    def getInfo(self):
        # 取账号信息
        account_info = self.xt_trader.query_stock_asset(self.xt_acc)
        result = {
            'available_cash': account_info.m_dCash,  # 取可用资金

        }
        hasInfo = {}
        # 查账号持仓
        positions = self.xt_trader.query_stock_positions(self.xt_acc)
        # 取各品种 总持仓 可用持仓
        for i in positions:
            if hasInfo.get(i.stock_code) is None:
                hasInfo[i.stock_code] = {}
            hasInfo[i.stock_code]['has'] = i.m_nVolume
            hasInfo[i.stock_code]['canSell'] = i.m_nCanUseVolume

        print('账户信息',result, hasInfo)
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
                    self.xt_trader.cancel_order_stock_async(self.xt_acc, order.order_id)

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

    def formateCode(self, code):
        if code[0] in ['6']:
            return  code + '.SH'
        if code[0] in ['0', '3']:
            return  code +'.SZ'
        if code[0:2] in ['51']:
            return code + '.SH'
        if code[0:3] in ['159']:
            return code + '.SZ'
        return code
    def startBuy(self):
        self.get_xttrader()
        info, hasInfo = self.getInfo()
        data = fetchPost('/drawServer/getSellCodes', {})
        print(data)
        # 添加已持有的股票
        # codes = {i: 1 for i in hasInfo.keys()}
        # self.codes = [i for i in codes.keys()]
        if data is not None:
            for code in data['data']:
                code_ = self.formateCode(code)
                if code_ in self.codes:
                    continue
                self.codes.append(code_)

        print('codes',self.codes)
        globalData['startBuy'] = True
        # self.buyNext()

    def buyNext(self):
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
        if stockCache.get(code) is None:
            stockData = CacheStock(code)
            stockCache[code] = stockData
        else:
            stockData = stockCache.get(code)
        return stockData
    def buy(self, code):
        if self.hasBuyDoing(code):
            return
        stockData = self.getStockData(code)

        info, hasInfo = self.getInfo()
        buyItem = stockData.getBuyItem(info, hasInfo)
        if buyItem:
            data = buyItem['data']
            print(code, 'buy',buyItem)
            full_tick = stockData.getLastData()
            buyValue = min(data['buyValue'], full_tick['lastPrice'])
            if data['buyNum'] > 0:
                async_seq = self.xt_trader.order_stock_async(self.xt_acc, code, xtconstant.STOCK_BUY, data['buyNum'], xtconstant.FIX_PRICE,
                                                buyValue,
                                                'buy', code)


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
        pass
    def sell(self, code, info, hasInfo):
        stockData = self.getStockData(code)
        sellItem = stockData.getSellItem(info, hasInfo)
        if sellItem:
            data = sellItem['data']
            full_tick = stockData.getLastData()
            print(code, 'sell', sellItem)
            sellValue = max(data['sellValue'], full_tick['lastPrice'])
            if data['sellNum'] > 0:
                async_seq = self.xt_trader.order_stock_async(self.xt_acc, code, xtconstant.STOCK_SELL, data['sellNum'],
                                                        xtconstant.FIX_PRICE,
                                                        sellValue,
                                                        'sell', code)

    # 是交易日
    def isTranding(self, code):
        now = datetime.now()
        dataItem = self.getLastData(self.formateCode(code))
        if dataItem is None:
            return False
        if now.strftime('%Y%m%d') == dataItem['timetag'].split(' ')[0]:
            return True

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
    data = xtdata.get_local_data ([], ['000816.SZ'], period='1m', count=10)
    print(data)
if __name__ == '__main__':
    # 迅投研 xtquant 示例
    now = datetime.now()
    stockBuySell = StockBuySell()
    globalData['stockBuySell'] = stockBuySell
    stockBuySell.hasBuyDoing('')
    startStr = ' 09:30:00'
    endStr = ' 15:00:00'

    # test()

    startDate = datetime.fromisoformat(now.strftime('%Y-%m-%d') + startStr)
    endDate = datetime.fromisoformat(now.strftime('%Y-%m-%d') + endStr)
    if startDate < now < endDate:
        if stockBuySell.isTranding('000816'):
            stockBuySell.startBuy()
    while True:
        now = datetime.now()
        startDate = datetime.fromisoformat(now.strftime('%Y-%m-%d') + startStr)
        endDate = datetime.fromisoformat(now.strftime('%Y-%m-%d') + endStr)
        if endDate < now or now < startDate or [6].index(now.isoweekday()):
            stockBuySell.codes = []
            globalData['startBuy'] = False
            stockCache = {}
            pass
            continue

        if startDate < now < endDate:
            print('doSell', now)
            stockBuySell.doSell()
            if globalData['startBuy']:
                if len(stockBuySell.codes) > 0:
                    stockBuySell.buyNext()
                stockBuySell.cancelSell_Buy()
                print('=============', datetime.now().timestamp() - now.timestamp())


        if now.strftime('%H:%M:%S') == startDate.strftime('%H:%M:%S'):
            if stockBuySell.isTranding('000816'):
                stockBuySell.startBuy()
        if (1- (datetime.now().timestamp() - now.timestamp())) > 0:
            time.sleep(1- (datetime.now().timestamp() - now.timestamp()))
    # 死循环 阻塞主线程退r

    # xtdata.run()
