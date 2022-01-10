import tushare as ts
import requests
import json
import time
from datetime import datetime
from urllib import parse
import threading
import pymongo
from hack.include import list as m_list
import os
# import hack.include as m_list
import hack.util as util
ts.set_token('7c797390e1c7caa6f79aadc01e4ad3577707f240c052f9b682f6782f')
def get_realtime_quotes(code):
    df = ts.get_realtime_quotes(code)  # Single stock symbol
    names=['ask','bid']
    for i in range(1,5):
        names.append('b%d_v'%i)
        names.append('b%d_p' % i)
        names.append('a%d_v' % i)
        names.append('a%d_p' % i)

    try:
        df=df[names]
        df.astype('float')
        result=df.to_dict(orient="records")[0]
    except TypeError as e:
        print(e)
        result={}
    for i in result:
        result[i]=float(result[i])
    return result

def describe(self):
    des = self.mydb['describe']
    insert={
        "f1":"",
        "f2": "最新价",
        "f3": "涨跌幅",#%
        "f4": "涨跌额",
        "f5": "成交量（手）",
        "f6": "成交额",
        "f7": "振幅",
        "f8": "换手率",
        "f9": "市盈率（动态）",
        "f10": "量比",
        "f11": "",
        "f12": "股票代码",
        "f13": "",
        "f14": "股票名",
        "f15": "最高",
        "f16": "最低",
        "f17": "今开",
        "f18": "昨收",
        "f20": "",
        "f21": "",
        "f22": "",
        "f23": "市净率",
        "f24": "",
        "f25": "",
        "f62": "",
        "f115": "",
        "f128": "",
        "f136": "",
        "f140": "",
        "f141": "",
        "f152": "",
    }

threadLock = threading.Lock()
class Stock:
    stock_describe = {
        "f11": "买五",
        "f12": "成交数",
        "f13": "买四",  # %
        "f14": "",
        "f15": "买三",
        "f16": "",
        "f17": "买二",
        "f18": "",
        "f19": "买一",
        "f20": "",
        "f31": "卖五",
        "f32": "",
        "f33": "卖四",
        "f34": "",
        "f35": "卖三",
        "f36": "",
        "f37": "卖二",
        "f38": "",
        "f39": "卖一",
        "f40": "",
        "f43": "最新",
        "f44": "最高",
        "f45": "最低",
        "f46": "今开",
        "f47": "总手",
        "f48": "金额",
        "f49": "外盘",
        "f50": "量比",
        "f52": "跌停",
        "f57": "编号",
        "f58": "股票名",
        "f60": "昨收",
        "f71": "均价",
        "f127": "行业板块",
        "f128": "地域板块",
        "f135": "主力流入",
        "f136": "主力流出",
        "f137": "主力净流入",
        "f138": "超大流入",
        "f139": "超大流出",
        "f141": "大单流入",
        "f142": "大单流出",
        "f144": "中单流入",
        "f145": "中单流出",
        "f147": "小单流入",
        "f148": "小单流出",
        "f161": "内盘",
        "f168": "换手率",
        "f169": "涨跌",
        "f170": "涨幅",
    }

    def __init__(self,maxthreading=1000):
        # 不可太小，其他程序也会占用线程数
        self.threadingNum=maxthreading


        myclient = pymongo.MongoClient("mongodb://localhost:27017/")
        self.mydb = myclient["dongfangcaifu"]
        self.url="http://6.push2.eastmoney.com/api/qt/clist/get"
        self.menu=self.get_menu()
        self.param = {
            'cb': 'jQuery112407522976605656146_' + str(int(time.time())),
            'pn': 1,
            'pz': 20,
            'po': 1,
            'np': 1,
            # 'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': 'm:1 s:2',
            'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152,f45',
            '_': int(time.time())
        }
        self.headers={
            'Host': 'push2.eastmoney.com',
            'Referer':'http://quote.eastmoney.com/',
            "User-Agent":'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'
        }
        self.threads=[]
        self.stocks=[]
        self.get_stocks()
        # 等待线程执行结束
        self.waiter()
        # self.threadingNum += threading.activeCount()

    def __del__(self):
        for i in self.threads:
            pass;
        self.threads.clear()
    def get_menu(self):
        url='http://quote.eastmoney.com/center/api/sidemenu.json'
        res=requests.get(url=url)
        data=[]

        if res.status_code==200:
            data=json.loads(res.text)
        return data

    def get_stocks(self):
        # 通过概念板块分类爬取
        def get(item,page=1):
            current = datetime.now()

            self.param['fs'] = 'b:%s f:!50' % item.get("key").split(".")[-1]
            self.param['-'] = int(current.timestamp())
            self.param['pn'] = page
            self.param['cb'] = 'jQuery112407522976605656146_' + str(int(current.timestamp()))
            # print(self.param)
            url = self.url + "?" + parse.urlencode(self.param)
            res = requests.get(url)
            if res.status_code == 200:
                data = json.loads(res.text[res.text.find("{"):-2])

                if data.get('data') is not None:
                    for da in data.get('data').get("diff"):
                        threadLock.acquire()
                        if m_list.find(self.stocks,da['f12']) is False:
                            self.stocks.append(da['f12'])
                        threadLock.release()
                    page+=1
                    get(item,page)
        menus=self.find(["沪深京板块",'概念板块'])
        for menu in menus:
            self.run(get,menu,1)

    def waiter(self):
        for i in self.threads:
            i.join()
        self.threads.clear()

    def find(self,title,menu=None):
        if menu is None:
            menu=self.menu
        if type(title)==list:
            for t in title:

                menu=self.find(t,menu)
                if menu is None:
                    break
                menu=menu.get("next",menu)
            return menu

        result=None
        for item in menu:
            if item.get('title')==title:
                result=item
                break
        return result

    def insert_mongo(self,code):
        current = datetime.now()
        doc=self.marketAnalysis(code,current)
        doc = util.getKeys_dic(doc, self.stock_describe.keys())
        if doc is not None:
            doc["time"] = current
            names = self.mydb['names']
            if names.find_one({'code': doc['f57']}) is None:
                names.insert_one({'code': doc['f57'], 'name': doc['f58']})
            colloction=self.mydb[doc['f57']]

            colloction.insert_one(doc)

    def run(self,fun,*args):
        temp = threading.Thread(target=fun, args=args)
        temp.start()
        self.threads.append(temp)
        while True:
            activeCount = threading.activeCount()
            if activeCount< self.threadingNum:
                break
            time.sleep(1)
            print("可活动线程数：%d"%self.threadingNum)
            print("活动线程数：%d"%activeCount)

    def do(self,insert=None):
        for stock in self.stocks:
            if insert is not None:
                self.run(insert, stock)


    # 行情
    def marketAnalysis(self,code='',current=None):
        url='http://push2.eastmoney.com/api/qt/stock/get'
        param={
            'invt': 2,
            'fltt': 2,
            'secid': '0.%s'%code,
            # 'ut': 'fa5fd1943c7b386f172d6893dbfba10b'
        }
        if current is None:
            current = datetime.now()
        param['-'] = int(current.timestamp())
        # param['fields'] = ','.join(describe.keys())
        param['fields'] = "f43,f57,f58,f169,f170,f46,f44,f51,f168,f47,f164,f163,f116,f60,f45,f52,f50,f48,f167,f117,f71,f161,f49,f530,f135,f136,f137,f138,f139,f141,f142,f144,f145,f147,f148,f140,f143,f146,f149,f55,f62,f162,f92,f173,f104,f105,f84,f85,f183,f184,f185,f186,f187,f188,f189,f190,f191,f192,f107,f111,f86,f177,f78,f110,f260,f261,f262,f263,f264,f267,f268,f250,f251,f252,f253,f254,f255,f256,f257,f258,f266,f269,f270,f271,f273,f274,f275,f127,f199,f128,f193,f196,f194,f195,f197,f80,f280,f281,f282,f284,f285,f286,f287,f292,f293,f181,f294,f295,f279,f288"

        param['cb'] = 'jQuery112407522976605656146_' + str(int(current.timestamp()))
        url+="?"+parse.urlencode(param)
        res=requests.get(url=url,headers=self.headers)
        print(res.text)
        if res.status_code == 200:
            data = json.loads(res.text[res.text.find("{"):-2])
            return data.get('data')
        return None




if __name__ == '__main__':
    stock=Stock()

    ti=time.time()
    #
    # print()
    print(stock.stocks)
    # stock.insert_mongo('002038')
    stock.do(stock.insert_mongo)
    stock.waiter()
    print(time.time()-ti)
    # te = os.system('netstat -nap')

    # 查看端口对于进程 lsof -i:5000
    # 杀死对应端口 kill -9 PID
    # print(te)

    print()
    # stock.marketAnalysis()