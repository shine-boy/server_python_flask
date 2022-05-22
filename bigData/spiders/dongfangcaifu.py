import scrapy
import time
from urllib import parse
import json
import math
import requests
from hack.util import mongodb_connect
import hack.include.stock as stock
from datetime import datetime
class dongfang(scrapy.Spider):
    name='dongfangcaifu'

    def __init__(self):
        myclient = mongodb_connect()
        self.mydb = myclient["dongfangcaifu"]
        pass

    def start_requests(self):
        types=[
            {
                'url':"http://93.push2.eastmoney.com/api/qt/clist/get",
                'type':"上证系列指数",
                'fs': 'm:1 s:2',
            },
            {
                'url': "http://93.push2.eastmoney.com/api/qt/clist/get",
                'type': "深证系列指数",
                'fs': 'm:1 s:5',
            }
            ,
            {
                'url': "http://93.push2.eastmoney.com/api/qt/clist/get",
                'type': "中证系列指数",
                'fs': 'm:2',
            }
        ]
        param={
            'cb': 'jQuery112407522976605656146_'+str(int(time.time())),
            'pn': 1,
            'pz': 20,
            'po': 1,
            'np': 1,
            # 'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': 'm:1 s:2',
        'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f26,f22,f33,f11,f62,f128,f136,f115,f152',
        '_': int(time.time())
        }
        # type=types[0]
        for type in types:
            param['fs']=type['fs']
            url = type['url']+"?"+parse.urlencode(param)
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parsePage,meta={"param":param,'url':type['url']})


    def describe(self):
        des = self.mydb['describe']
        insert={
            "f1","",
            "f2", "最新价",
            "f3", "涨跌幅",#%
            "f4", "涨跌额",
            "f5", "成交量（手）",
            "f6", "成交额",
            "f7", "振幅",
            "f8", "换手率",
            "f9", "市盈率（动态）",
            "f10", "量比",
            "f11", "",
            "f12", "股票代码",
            "f13", "",
            "f14", "股票名",
            "f15", "最高",
            "f16", "最低",
            "f17", "今开",
            "f18", "昨收",
            "f20", "",
            "f21", "",
            "f22", "",
            "f23", "市净率",
            "f24", "",
            "f25", "",
            "f62", "",
            "f115", "",
            "f128", "",
            "f136", "",
            "f140", "",
            "f141", "",
            "f152", "",
        }
        if des.find_one({'table': "fund"}) is None:
            des.insert_one(insert)

    def parsePage(self, response):
        text=response.text
        res=json.loads(text[text.find("{"):-2])


        total=res['data']['total']
        param=response.meta['param']

        for i in range(1,math.ceil(total/param['pz'])+1):
            param['pn']=i
            current=datetime.now()
            param['-'] = int(current.timestamp())
            url = response.meta['url']+"?"+parse.urlencode(param)

            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse,meta={"time":current})


    def parse(self,response):
        text = response.text
        res = json.loads(text[text.find("{"):-2])
        data=res['data']['diff']
        current=response.meta['time']
        for doc in data:
            names = self.mydb['names']
            if names.find_one({'code': doc['f12']}) is None:
                names.insert_one({'code': doc['f12'], 'name': doc['f14']})
            colloction=self.mydb[doc['f12']]

            doc.update(stock.get_realtime_quotes(doc['f12']))
            doc["time"] = current
            colloction.insert_one(doc)

if __name__ == '__main__':
    d=dongfang()
    print(list(d.mydb['931144'].find()))