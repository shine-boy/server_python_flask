import datetime
import math
import random
import numpy as np
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn import tree
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVR
import joblib
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import metrics
from hack.util import mongodb_connect
def productTest ():
  total = 1000
  result = [10]
  pre = result[0]
  r = 0.1
  for i in range(1,total):
    flag = 1 if random.random() > 0.5  else -1
    pre = pre + random.random() * r * flag
    result.append(pre)
  return result


# 线性回归
def line(train_data, test_data, train_target, test_target):
    lr = LinearRegression()
    lr.fit(train_data, train_target)
    score = lr.score(test_data, test_target)
    # 进行预测
    print('得分', score)
    pass

# 线性核函数
def linSVR(train_data, test_data, train_target, test_target):
    lr = LinearSVR(C=2)
    lr.fit(train_data, train_target)
    score = lr.score(test_data, test_target)

    # 进行预测
    # print('预测值：', lr.predict(test_data), '实际值', test_target)
    print('得分', score)

# 高斯核函数
def gaoSiSVR(train_data, test_data, train_target, test_target):
    lr = SVR(kernel='rbf',C=10,gamma=0.1,coef0=0.1)
    lr.fit(train_data, train_target)
    score = lr.score(test_data, test_target)

    # 进行预测
    # print('预测值：', lr.predict(test_data), '实际值', test_target)
    print('得分', score)


# 持续学习回归器
def onlineReg(train_data, train_target, modelPath, type='train'):

    if os.path.exists(modelPath) is True:
        # 加载模型
        lr = joblib.load(modelPath)
    else:
        lr = SGDRegressor(eta0=0.0001)
        # lr = SVR(kernel='rbf',C=10,gamma=0.1,coef0=0.1)
    if type == 'train':
        lr.partial_fit(train_data, train_target)
        # lr.fit(train_data, train_target)
        # 保存模型
        joblib.dump(lr, modelPath)
        score = lr.score(train_data, train_target)
        print('得分', score)
    else:
        pre = lr.predict(train_data)
        return pre

#  eg: https://blog.csdn.net/qq_41897304/article/details/121777109?spm=1001.2014.3001.5502
def stock():
    testData = productTest()
    l = 4
    X = []
    y = []
    for i in range(l + 1, len(testData)):
        temp = []
        for j in range(l):
            temp.append(testData[i - 1 - l + j])
        X.append(temp)
        y.append(testData[i])

    # 数据预处理
    train_data, test_data, train_target, test_target = train_test_split(np.array(X), np.array(y), test_size=0.3)
    Stand_X = StandardScaler()  # 特征进行标准化
    Stand_Y = StandardScaler()  # 标签也是数值，也需要进行标准化
    train_data = Stand_X.fit_transform(train_data)
    test_data = Stand_X.transform(test_data)
    train_target = Stand_Y.fit_transform(train_target.reshape(-1, 1))  # reshape(-1,1)指将它转化为1列，行自动确定
    test_target = Stand_Y.transform(test_target.reshape(-1, 1))

    # line(train_data, test_data, train_target, test_target)
    # linSVR(train_data, test_data, train_target, test_target)
    # gaoSiSVR(train_data, test_data, train_target, test_target)
    # onlineReg(train_data,  train_target, Stand_Y)
    onlineReg(test_data, test_target,Stand_Y)


def loadCsv(pathName):
    df = pd.read_csv(pathName, encoding="utf-8")
    df_array = np.array(df)  # 将pandas读取的数据转化为array
    df_list = df_array.tolist()  # 将数组转化为list
    return {
        "list": df_list,
        "columns": np.array(df.columns),
    }

def listToObjList(lis, columns, back=None) :
    result = []
    for li in lis:
        temp = {}
        i = 0
        for column in columns:
            temp[column] = li[i]
            i+=1
        if back is not None:
            temp = back(temp)
        result.append(temp)
    # print(result[0])
    return result



class Stock:
    l = 4
    stand_X = StandardScaler()  # 特征进行标准化
    stand_Y = StandardScaler()
    standXPath = './files/stock_standX.pkl'
    standYPath = './files/stock_standY.pkl'
    modelPath = './files/stock_model.pkl'
    name = 'stock'
    def __init__(self):
        myclient = mongodb_connect()
        self.mydb = myclient["dongfangcaifu"]
        pass

    def getCodes(self):
        names = self.mydb['names']
        return [doc['code'] for doc in names.find()]

    def get_all_data(self):
        codes = self.getCodes()
        X,y = [], []
        for code in codes:
            stockDb = self.mydb[code]
            data = [doc for doc in stockDb.find().sort('date', 1)]
            l = len(data)
            X_, y_ = self.loadData(data)
            X.extend(X_)
            y.extend(y_)
        return X,y


    def getStand(self, pathName):
        if os.path.exists(pathName) is True:
            # 加载模型
            return joblib.load(pathName)
        else:
            return StandardScaler()  # 特征进行标准化

    def loadData(self, data):
        X = []
        y = []
        for i in range(self.l, len(data)):
            self.format(data[i])
            temp = [data[i].get('Days')]
            # temp.append(data[i-1].get('volume'))
            for j in range(self.l):
                temp.append(data[i - self.l + j].get('close')*(j+1))
                # temp.append(data[i - self.l + j].get('high'))
                # temp.append(data[i - self.l + j].get('low'))
            temp.append(data[i - 1].get('low'))
            temp.append(data[i - 1].get('high'))
            X.append(temp)
            y.append(data[i].get('close'))
        return X, y

    def getDataObj(self, s):
        temp = {}
        s = str(s)
        def formate(tem):
            for key in tem:
                tem[key] = int(tem[key])
            return tem
        try:
            res = re.search('(?P<year>\d{4})[/-](?P<month>\d{1,2})[/-](?P<day>\d{1,2})', s)
            if res is not None:
                temp = res.groupdict()
                return formate(temp)
            res = re.search('(?P<month>\d{1,2})[/-](?P<day>\d{1,2})[/-](?P<year>\d{4})', s)
            if res is not None:
                temp = res.groupdict()
                return formate(temp)
            res = re.search('^(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})$', s)
            if res is not None:
                temp = res.groupdict()
                return formate(temp)
            res = re.search('(?P<time>\d{10})(\.0)?', s)
            if res is not None:
                cur = datetime.datetime.fromtimestamp(int(res.groupdict()['time']))
                temp['year'] = cur.year
                temp['month'] = cur.month
                temp['day'] = cur.day
                return temp
            raise Exception('类型错误', s)
        except Exception as e:
            print(s)
            raise e

    def formateDate(self, data):
        try:
            tempData = self.getDataObj(data['date'])
            cur = datetime.datetime.strptime('%d/%d/%d' % (tempData['month'], tempData['day'], tempData['year']),
                                             "%m/%d/%Y")
            data['Days'] = cur.weekday() + 1
            data['date'] = cur
        except Exception as e:
            print(data)

            print(e)
            raise e
        finally:
            return data

    def format(self, data):
        self.formateDate(data)
        return data

    def trianStock(self):

        X, y = self.get_all_data()

        print(len(X))
        train_data = self.stand_X.fit_transform(np.array(X))
        train_target = self.stand_Y.fit_transform(np.array(y).reshape(-1, 1))  # reshape(-1,1)指将它转化为1列，行自动确定
        # 保存模型
        joblib.dump(self.stand_Y, self.standYPath)
        joblib.dump(self.stand_X, self.standXPath)
        try:
            onlineReg(train_data, train_target, self.modelPath)
        except Exception as e:
            # print(X)
            raise e

    def predictStock(self, data):
        X, Y = self.loadData(data)
        train_data = self.stand_X.transform(np.array(X))
        try:
            pre = onlineReg(train_data,  [], self.modelPath, 'predict')
            preValue = self.stand_Y.inverse_transform([pre])
            print(self.name, 'predict', preValue)
            return preValue
        except Exception as e:
            print(X)
            raise e


class StockClose(Stock):
    standXPath = './files/stockClose_standX.pkl'
    standYPath = './files/stockClose_standY.pkl'
    modelPath = './files/stockClose_model.pkl'
    name = 'close'
    def __init__(self):
        super().__init__()
        self.stand_X = self.getStand(self.standXPath)
        self.stand_Y = self.getStand(self.standYPath)
        pass

class StockLow(Stock):
    standXPath = './files/stockLow_standX.pkl'
    standYPath = './files/stockLow_standY.pkl'
    modelPath = './files/stockLow_model.pkl'
    name = 'low'
    def __init__(self):
        super().__init__()
        self.stand_X = self.getStand(self.standXPath)
        self.stand_Y = self.getStand(self.standYPath)
        pass
    def loadData(self, data):
        X = []
        y = []
        for i in range(self.l, len(data)):
            self.format(data[i])
            temp = []
            temp.append(data[i].get('Days'))
            for j in range(self.l):
                temp.append(data[i - self.l + j].get('close')*(j+1))
                # temp.append(data[i - self.l + j].get('low'))
            temp.append(data[i - 1].get('change'))
            temp.append(data[i - 1].get('volatility'))
            X.append(temp)
            y.append(data[i].get('low'))
        return X, y


class StockHigh(Stock):
    standXPath = './files/stockHigh_standX.pkl'
    standYPath = './files/stockHigh_standY.pkl'
    modelPath = './files/stockHigh_model.pkl'
    name = 'high'
    def __init__(self):
        super().__init__()
        self.stand_X = self.getStand(self.standXPath)
        self.stand_Y = self.getStand(self.standYPath)
        pass

    def loadData(self, data):
        X = []
        y = []
        for i in range(self.l, len(data)):
            self.format(data[i])
            temp = []
            temp.append(data[i].get('Days'))
            for j in range(self.l):
                temp.append(data[i - self.l + j].get('close')*(j+1))
                # temp.append(data[i - self.l + j].get('high'))
            temp.append(data[i - 1].get('volatility'))
            temp.append(data[i - 1].get('change'))
            X.append(temp)
            y.append(data[i].get('high'))
        return X, y

class StockOpen(Stock):
    standXPath = './files/stockOpen_standX.pkl'
    standYPath = './files/stockOpen_standY.pkl'
    modelPath = './files/stockOpen_model.pkl'
    name = 'open'
    def __init__(self):
        super().__init__()
        self.stand_X = self.getStand(self.standXPath)
        self.stand_Y = self.getStand(self.standYPath)
        pass

    def loadData(self, data):
        X = []
        y = []
        for i in range(self.l, len(data)):
            self.format(data[i])
            temp = []
            temp.append(data[i].get('Days'))
            for j in range(self.l):
                temp.append(data[i - self.l + j].get('close')*(j+1))
                # temp.append(data[i - self.l + j].get('open'))
                # temp.append(data[i - self.l + j].get('high'))
            X.append(temp)
            y.append(data[i].get('open'))
        return X, y


def trainStock():
    # stockClose = StockClose()
    # stockClose.trianStock()
    stockLow = StockLow()
    stockLow.trianStock()
    stockHigh = StockHigh()
    stockHigh.trianStock()
    stockOpen= StockOpen()
    stockOpen.trianStock()

def predictStock():
    obj = {
        '601398': [
        {
            'date': '2024/7/19',
            'open': 5.90,
            'high': 5.82,
            'low': 5.82,
            'close': 5.91,
            'AdjClose': '',
            'volume': 3601400,
            'code': '601398',
            'Days': 5
        }, {
            'date': '2024/7/22',
            'open': 5.88,
            'high': 5.89,
            'low': 5.76,
            'close': 5.84,
            'AdjClose': '',
            'volume': 3230600,
            'code': '601398',
            'Days': 1
        }, {
            'date': '2024/7/23',
            'open': 5.82,
            'high': 6.06,
            'low': 5.81,
            'close': 6.01,
            'AdjClose': '',
            'volume': 5081400,
            'code': '601398',
            'Days': 2
        }, {
            'date': '2024/7/24',
            'open': 6,
            'high': 6.11,
            'low': 5.99,
            'close': 6.06,
            'AdjClose': '',
            'volume': 3184500,
            'code': '601398',
            'Days': 3
        }, {
            'date': '2024/7/25',
            'open': 6.05,
            'high': 6.12,
            'low': 5.97,
            'close': 6.06,
            'AdjClose': '',
            'volume': 4114800,
            'code': '601398',
            'Days': 4
        }],
        '000725': [
        {
            'date': '2024/7/19',
            'open': 4.03,
            'high': 4.09,
            'low': 4.02,
            'close': 4.07,
            'AdjClose': '',
            'volume': 3215700,
            'code': '601398',
            'Days': 5
        }, {
            'date': '2024/7/22',
            'open': 4.08,
            'high': 4.09,
            'low': 3.98,
            'close': 4.01,
            'AdjClose': '',
            'volume': 3230600,
            'code': '601398',
            'Days': 1
        }, {
            'date': '2024/7/23',
            'open': 4.01,
            'high': 4.01,
            'low': 3.90,
            'close': 3.90,
            'AdjClose': '',
            'volume': 4479000,
            'code': '601398',
            'Days': 2
        }, {
            'date': '2024/7/24',
            'open': 3.90,
            'high': 3.91,
            'low': 3.75,
            'close': 3.80,
            'AdjClose': '',
            'volume': 6061800,
            'code': '601398',
            'Days': 3
        }, {
            'date': '2024/7/25',
            'open': 3.76,
            'high': 3.80,
            'low': 3.75,
            'close': 3.78,
            'AdjClose': '',
            'volume': 3680500,
            'code': '601398',
            'Days': 4
        }],
    }
    for key in obj:
        print(key)
        testData = obj[key]
        stockClose = StockClose()
        stockClose.predictStock(testData)
        stockLow = StockLow()
        stockLow.predictStock(testData)
        stockHigh = StockHigh()
        stockHigh.predictStock(testData)


class Test():
    currentValue = 1000000
    increases = 0.01
    stockClose = StockClose()
    stockLow = StockLow()
    stockHigh = StockHigh()
    stockOpen = StockOpen()
    num = 0
    predicts = []
    sellLog = []
    buysLog = []
    def __init__(self):
        myclient = mongodb_connect()
        self.mydb = myclient["dongfangcaifu"]
        pass

    def getCodes(self):
        names = self.mydb['names']
        return [doc['code'] for doc in names.find()]

    # data长度为计算的长度 l= 4
    def predict(self, data, l=1):
        if l < 1:
            return
        if len(data) > self.stockClose.l + 1:
            data = data[-(self.stockClose.l+1):]
        elif len(data) < self.stockClose.l + 1:
            return
        lastDay = self.stockClose.formateDate(data[-1])
        nowData = lastDay['date']
        if lastDay['Days'] == 5:
            nowData = lastDay['date'] + datetime.timedelta(days=3)
        else:
            nowData += datetime.timedelta(days=1)
        currentDay = {
            'date': nowData,
            'open': self.stockOpen.predictStock(data)[0][0],
            'high': self.stockHigh.predictStock(data)[0][0],
            'low': self.stockLow.predictStock(data)[0][0],
            'close': self.stockClose.predictStock(data)[0][0],
            'AdjClose': '',
            'volume': 0,
            'code': '601398',
            'Days': nowData.weekday() + 1
        }
        self.stockClose.format(currentDay)

        print(data)
        print(currentDay)
        self.predicts.append(currentDay)
        data.append(currentDay)
        self.predict(data, l-1)

    def computeTow(self, data):
        if len(self.predicts) > 0:
            self.predicts.pop()
        self.predict(data, 2)
        lastActual = data[-2]
        currentDay = self.predicts[-2]
        tomorrowDay = self.predicts[-1]
        low = currentDay['low']
        todayHigh = currentDay['high']
        lastPreDay = None
        try:
            lastPreDay = self.predicts[-3]
        except:
            pass
        high = tomorrowDay['high']
        increases = (high - low) / low
        # print('today Low', low)
        # print('tomorrow High', high)
        if lastPreDay is not None:
            if lastPreDay['low'] > lastActual['high']:
                print('买太高了！')
            if lastPreDay['high'] < lastActual['low']:
                print('卖太低了！')
            if lastPreDay['high'] > lastActual['high']:
                # 回退
                try:
                    temp = self.sellLog.pop()
                    self.currentValue -= temp["total"]
                    self.num += temp["num"]
                except:
                    pass
            if lastPreDay['low'] < lastActual['low']:
                # 回退

                print(lastPreDay)
                print(lastActual)
                try:
                    temp = self.buysLog.pop()
                    self.currentValue += temp["total"]
                    self.num -= temp["num"]
                except:
                    pass
        print('--------------', increases)
        if increases > self.increases:
            num = ((self.currentValue // low) // 100) * 100
            if num == 0:
                return
            self.buysLog.append({
                "num": num,
                "value": low,
                "total": num * low,
                "date": currentDay["date"]
            })
            self.num += num
            buys = num * low
            self.currentValue -= buys
        elif high < todayHigh:
            self.sellLog.append({
                "num": self.num,
                "value": todayHigh,
                "total": self.num * todayHigh,
                "date": currentDay["date"]
            })
            self.currentValue += self.num * todayHigh
            self.num = 0

            pass

    def draw(self, data, xLabel, yLabels):
        xpoints = list(map(lambda item: item[xLabel], data))
        for label in yLabels:
            y = list(map(lambda item: item[label], data))
            plt.plot(xpoints, y, marker='o', label=label)
        plt.legend()
    def test(self):
        codes = self.getCodes()
        stockDb = self.mydb['601398']
        testData = [doc for doc in stockDb.find().sort('date', 1)]
        for item in testData:
            self.stockClose.formateDate(item)
        # c = loadCsv("C:\\Users\\w30038925\\Downloads\\Amazon_Historical_Data.csv")
        # testData = listToObjList(c["list"],
        #                          ['date', 'close', 'volume', 'open', 'high', 'low'], self.stockClose.format)
        # testData.reverse()
        actualData = testData[-30:]
        testData_= actualData
        lastDay = testData_[-1]

        for i in range(len(testData_)- self.stockClose.l-1):
            temp = testData_[i: i+ self.stockClose.l+1]
            self.computeTow(temp)
        plt.subplot(1, 2, 1)
        print(actualData[0])
        self.draw(actualData, 'date', ['low'])
        self.draw(self.predicts, 'date', ['low'])
        plt.title("bus")
        #
        # plt.subplot(1, 3, 2)
        # self.draw(actualData, 'date', ['high'])
        # self.draw(self.predicts, 'date', ['high'])
        # plt.title("sell")
        #
        plt.subplot(1, 2, 2)
        self.draw(actualData, 'date', ['close'])
        self.draw(self.predicts, 'date', ['close'])
        plt.title("Close")
        print(self.predicts)
        print(self.sellLog)
        print(self.buysLog)
        print(self.currentValue)
        print(self.num)
        print('total value', lastDay['open']*self.num + self.currentValue)
        plt.show()

# 连续升降
# mode:  0 严格模式， 1 松散模式
# increase: 0 下降， 1  上升
def persist_change(data,  persist=5, value_field='value', mode=0, increase = 0):
    # 浮动值
    f = 0.02
    increases = []
    l = len(data)
    for i in range(l-1, l-persist, -1):
        c = (data[i].get(value_field) - data[i-1].get(value_field)) / data[i-1].get(value_field)
        increases.append(c)
    increases.reverse()
    flags = [0,0]
    p = len(increases)
    for i in range(p):
        if increases[i]>0:
            flags[1]+=1
        elif increases[i]<0:
            flags[0]+=1
        else:
            flags[0]+=1
            flags[1]+=1
    if flags[0] == p and flags[1] == p:
        return []
    if mode == 0:
        if flags[increase] == p:
            return data[l-p-1:]
    else:
        # 允许浮动数
        fs = int((p+1)/5)
        for i in range(p):
            if increase == 0 and increases[i] > f:
                return []
            if increase == 1 and increases[i] < -f:
                print(increases[i])
                return []
        if flags[increase] >= p - fs:
            return data[l-p-1:]
    return []

# f: 浮动值
def find_same(target, source, value_field='value', f=0.001):

    def get_increases(data):
        l = len(data)
        increases = []
        for i in range(l - 1, 0, -1):
            c = (data[i].get(value_field) - data[i - 1].get(value_field)) / data[i - 1].get(value_field)
            increases.append(c)
        increases.reverse()
        return increases

    source_inc = get_increases(source)
    target_inc = get_increases(target)
    lt = len(target_inc)
    sl = len(source_inc)
    for i in range(0, sl-lt+1):
        t = i
        # 允许浮动数
        fs = int(len(target) / 5)
        print(fs)
        flag = True
        for j in range(lt):

            if math.fabs(target_inc[j] - source_inc[t]) > f:
                fs-=1
                flag = False
            else:
                if flag is False:
                    print('add')
                    fs+=1
                flag = True

            if fs <-1:
                break
            t+=1
        print(fs)
        if fs>=0:
            return source[i:i+lt+1]
    return []







if __name__ == '__main__':
    # stock()
    # trianStockClose()
    # trainStock()
    print(int(3/2))
    test = Test()
    test.test()
    # print(find_same([{"value": 1},{"value": 3},{"value": 2.98},{"value": 3},{"value": 5},{"value": 6}], [{"value": 1},{"value": 3},{"value": 2.987},{"value": 3},{"value": 5.01},{"value": 6} ,{"value": 34}]))
    print()
    pass

    # print(os.path.exists('./files/decision_tree_model.pkl'))