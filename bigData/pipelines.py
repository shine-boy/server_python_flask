# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
import os
import pandas as pd
import matplotlib.pyplot as plt
import codecs
import json
import logging
from collections import OrderedDict
import datetime
from scrapy.utils.project import get_project_settings
settings = get_project_settings()
class BigdataPipeline(object):
    # Monodb数据库的配置
    def __init__(self):
        to_day = datetime.datetime.now()
        self.filename = "itemText/item_{}_{}_{}.txt".format(to_day.year, to_day.month, to_day.day)

        connection = pymongo.MongoClient(
            settings['MONGODB_SERVER'],
            settings['MONGODB_PORT']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db[settings['MONGODB_COLLECTION']]

    # def process_item(self, item, spider):
    #     # try:
    #     time = item['listingStartDate']
    #     if time.find('年') != -1:
    #         time = time.replace('年', '-').replace('月', '-').replace('日', '')
    #         if time >= '2019-01-01':
    #             print('-----------------')
    #             self.collection.insert(dict(item))
    #         # except Exception:
    #
    #         file = codecs.open(self.filename, 'a', encoding='utf-8')
    #         line = json.dumps(OrderedDict(item), ensure_ascii=False, sort_keys=False) + "\n"
    #         file.write(line)
    #         file.close()
    #     return item

    def spider_closed(self, spider):
        # 爬虫一旦关闭，就会实现这个方法，关闭数据库连接
        self.collection.close()

    def process_item(self, item, spider):
        # lis=item["comments"]
        # temp = pd.DataFrame([item])
        # data=pd.DataFrame([item])
        # path='bigData/data/data.csv'
        # # print(os.path.exists(path))
        # if os.path.exists(path):
        #     data=pd.read_csv(path)
        #
        #     data=data.append(temp,ignore_index=True)
        # data.to_csv(path,index=False)
        print(item)
        item['time']=datetime.datetime.now()
        self.collection.delete_many({'id':item["id"]})
        self.collection.insert(dict(item))
        return item

    # def process_item(self, item, spider):
    #
    #     temp = pd.DataFrame([item])
    #     data=pd.DataFrame([item])
    #     path='bigData/data/data.csv'
    #     if item.get("source")=="上海联合产权交易所":
    #         path = 'bigData/data/shanghai.csv'
    #     # print(os.path.exists(path))
    #     if os.path.exists(path):
    #         data=pd.read_csv(path)
    #         data=data.append(temp,ignore_index=True)
    #     data.to_csv(path,index=False)
    #
    #     return item
