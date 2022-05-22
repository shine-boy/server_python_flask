# coding: utf-8
# 东方财富基金
import scrapy
import time
from urllib import parse
from hack.util import mongodb_connect
import demjson
class fund(scrapy.Spider):
    name = 'dfcf_fund'

    def __init__(self):
        myclient = mongodb_connect
        db = myclient["stock_fund"]
        self.mydb = db['fund']
        self.url = 'http://fund.eastmoney.com/Data/Fund_JJJZ_Data.aspx'
        self.obj = {
            0: 'code',
            1: 'name',
            2: 'simpleNmae',
            3: '单位净值',
            4: '累计净值',
            7: '日增长值',
            8: '日增长率',
            17: '手续费'
        }
        pass


    def start_requests(self):


        param = {
            't':1,
            'lx':1,
            'letter':'',
            'gsid':'',
            'text':'',
            'sort':'zdf,desc',
            'page':'2,200',
            'dt':int(time.time()),
            'atfc':'',
            'onlySale':0
        }
        # type=types[0]

        url = self.url+"?"+parse.urlencode(param)
        yield scrapy.Request(url=url, dont_filter=True, callback=self.parsePage,meta={"param":param})


    def describe(self):
        des = self.mydb['describe']
        if des.find_one({'source': "东方财富"}) is None:
            des.insert_one(self.obj)

    # 获取总页数
    def parsePage(self, response):
        text=response.text
        params = response.meta['param']
        res=demjson.decode(text[text.find("{"):])
        pages = int(res['pages'])

        for i in range(1,pages + 1):
            params['page'] = str(i) + ',200'
            url = self.url + "?" + parse.urlencode(params)
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse)

    # 获取数据，存数
    def parse(self, response):
        text = response.text
        res = demjson.decode(text[text.find("{"):])
        showDay = res['showday']
        datas = res['datas']
        for i in range(len(datas)):
            data = datas[i]
            temp = {}
            for key in self.obj.keys():
                temp[str(key)] = data[key]
            temp['data'] = showDay[0]
            self.mydb.insert_one(temp)



