# -*- coding: utf-8 -*-
import codecs

import scrapy
import pytz
import json
import datetime
import os
from bigData.items import BigdataItem
from bigData.util.util import Util

class GqSpider(scrapy.Spider):
    name = 'mode'
    allowed_domains = ['www.jscq.com.cn']
    start_urls = ['http://www.jscq.com.cn/']

    def __init__(self, page=0, *args, **kwargs):
        super(GqSpider, self).__init__(*args, **kwargs)
        self.attributes = ['id', 'class']
        self.page = page
        self.maxPage = 0
        self.tz = pytz.timezone('Asia/Shanghai')
        # 代理服务器
        self.proxyHost = "ip4.hahado.cn"
        self.proxyPort = "44434"

        # 代理隧道验证信息
        self.proxyUser = "164002"
        self.proxyPass = "164002"

        self.proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
            "host": self.proxyHost,
            "port": self.proxyPort,
            "user": self.proxyUser,
            "pass": self.proxyPass,
        }

        self.proxies = {
            "http": self.proxyMeta,
            "https": self.proxyMeta,
        }

        self.filename = 'jsgq.txt'

    def start_requests(self):
        # 拼接页数
        url = 'http://www.jscq.com.cn/dsf/gq/jygg/index.html'

        yield scrapy.Request(url=url, dont_filter=True, callback=self.parse_page,
                             meta={'proxy': self.proxyMeta})

    def parse_page(self, response):
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        url = 'http://www.jscq.com.cn/dsf/gq/jygg/index.html'

        url_last = response.xpath('//div[@class="content_right_page"]/a')[-1].xpath('@href').extract_first()
        maxPage = url_last.split('.html')[0].replace('index_', '')
        self.maxPage = int(maxPage)
        yield scrapy.Request(url=url, dont_filter=True, callback=self.parse)

    def parse(self, response):
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)

        results = response.xpath('//table/tr[@style="height:36px;"]')

        # for res in results:
        res =results[0]
        url = "http://www.jscq.com.cn/dsf/gq/jygg/" + res.xpath('td')[1].xpath('a/@href').extract_first().replace(
            './', '')
        floorPrice = res.xpath('td')[3].xpath('string(.)').extract_first()
        # print(res.xpath('td')[2].xpath('./attribute::rowspan').extract_first())
        # print(res.xpath('td')[:1])

        yield scrapy.Request(url=url, dont_filter=True, callback=self.parse_one,
                             meta={'floorPrice': floorPrice, 'proxy': self.proxyMeta})


        #
        # if self.page < self.maxPage:
        #
        #     # 拼接页数
        #     nextpage_p1 = "http://www.jscq.com.cn/dsf/gq/jygg/index"
        #     self.page = self.page + 1
        #     nextpage = nextpage_p1 + "_" + str(self.page) + ".html"
        #     yield scrapy.Request(url=nextpage, dont_filter=True, callback=self.parse,
        #                             meta={'proxy':self.proxyMeta},
        #                             headers={'User-Agent': "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.5"})


    # 得到节点属性
    def getAttribute(self,node):
        attribute = {}
        for li in self.attributes:
            temp=node.xpath('./attribute::'+li).extract_first()
            if Util.isNull(temp) is False:
                attribute[li] = temp
        return attribute

    # 获取节点路径
    def getPath(self, ancestors):
        path = ''
        for node in ancestors:
            path = path + '/' + node['name']
            if Util.isNull(node['attribute'].get('id')) is False:
                path = path + '[@id="'+ node['attribute'].get('id') + '"]' + '[' + str(node['index']) + ']'
            elif Util.isNull(node['attribute'].get('class')) is False:
                path = path + '[@class="'+ node['attribute'].get('class') + '"]'+ '[' + str(node['index']) + ']'
            else:
                path = path + '[' + str(node['index']) + ']'
        print(path)
        return path


        # 祖节点中离目标结点最近的节点id和id之后的路径
    def getId(self, ancestors):
        path = ''
        id = ''
        i = 0
        for node in ancestors:
            id = node['attribute'].get('id')
            if Util.isNull(id) is False:
                path = '//'
                path = path + '[@id="' + node['attribute'].get('id') + '"]' + '[' + str(node['index']) + ']'
                path = path + self.getPath(ancestors[i:])
                break
            i += 1
        if Util.isNull(path):
            path = self.getPath(ancestors)

        return id, path

        # 祖节点中离目标结点最近的节点class
    def getClass(self, ancestors):
        path = ''
        className = ''
        i = 0
        for node in ancestors:
            className = node['attribute'].get('class')
            if Util.isNull(className) is False:
                path = '//'
                path = path + '[@class="' + node['attribute'].get('class') + '"]' + '[' + str(node['index']) + ']'
                path = path + self.getPath(ancestors[i:])
            i += 1
        if Util.isNull(path):
            path = self.getPath(ancestors)
        return className, path

    # 数组长度大第i个，否则不取
    def getTrue(self, lis, index=0, default=None):
        if len(lis) > index:
            return lis[index]
        return default

    # 得到所有祖节点 index表示获取祖结点的下标数
    def getAncestor(self,node):
        ancestor = node.xpath('./ancestor::*')
        ancestors = []
        for anc in ancestor:
            temp = {}
            attribute = self.getAttribute(anc)
            temp.setdefault('attribute', attribute)
            temp.setdefault('name', anc.xpath('name()').extract_first())
            if attribute.get('id') is not None:
                temp.setdefault('index', len(anc.xpath('./preceding-sibling::' + temp['name'] + '[@id="' + attribute.get('id') + '"]')) + 1)
            elif attribute.get('class') is not None:
                temp.setdefault('index', len(anc.xpath('./preceding-sibling::' + temp['name'] + '[@class="' + attribute.get('class') + '"]')) + 1)
            else:
                temp.setdefault('index', len(anc.xpath('./preceding-sibling::' + temp['name']))+1)
            ancestors.append(temp )
        node_={}
        attribute = self.getAttribute(node)
        node_.setdefault('attribute', self.getAttribute(node))
        node_.setdefault('name', node.xpath('name()').extract_first())
        if attribute.get('id') is not None:
            node_.setdefault('index', len(
                node.xpath('./preceding-sibling::' + node_['name'] + '[@id="' + attribute.get('id') + '"]')) + 1)
        elif attribute.get('class') is not None:
            node_.setdefault('index', len(
                node.xpath('./preceding-sibling::' + node_['name'] + '[@class="' + attribute.get('class') + '"]')) + 1)
        else:
            node_.setdefault('index', len(node.xpath('./preceding-sibling::' + node_['name'])) + 1)
        ancestors.append(node_)
        return ancestors


    def findTarget(self, node, obj,index=0):
        ancestors = obj.get('ancestor')
        flag = True
        result=''
        try:
            if flag:
                print('hfhf')
                path = self.getPath(ancestors)
                target = node.xpath(path)
                if len(target) > 0:
                    if index > 0:
                        target = target[index]
                    result = target
                    flag = False
            elif flag:
                # 以id索引
                id, path = self.getId(ancestors)

                target = node.xpath("//*[@id='" + id + "']")
                if len(target) > 0:
                    target = target[0].xpath(path)
                    if len(target) > 0:
                        if index > 0:
                            target = target[index]
                        result = target
                        flag = False
            else:
                # 以class索引
                classNames, path = self.getClass(ancestors)
                if len(classNames) > 0:
                    target = node.xpath("//*[@class='" + classNames[0] + "']")
                    if len(target) > 0:
                        target = target[0]
                        if len(classNames) > 1:
                            for cla in classNames[1:]:
                                target = target.xpath("./*[@class='" + cla + "']")
                            target = node.xpath("//*[@id='" + id + "']")
                            if len(target) > 0:
                                target = target[0].xpath(path)
                                if len(target) > 0:
                                    if index > 0:
                                        target = target[index]
                                    result = target
                                    flag = False
            return result
        except Exception as e:
            print('findtarget')
            print(e)
        return None

    def getTarget(self, node, obj,index=0):
        ancestors = obj.get('ancestor')
        if type(obj.get('value')) == list:
            # 为结果为list,type为dict型
            if obj.get('type') == 'dict':
                lis = []
                try:
                    temp = {}
                    for va in obj.get('value'):
                        temp.setdefault(va.get('key'),self.getTarget(node, va))
                    lis.append(temp)
                    return lis
                except Exception as e:
                    print(e)
                    print('结果为list,type为dict型')
            # 为结果为list,type为list型
            elif obj.get('type') == 'list':
                lis = []
                try:
                    target = self.findTarget(node, obj)
                    for va in obj.get('value'):
                        if len(target) > 0:
                            target_ = target[0].xpath('./child::*')
                            indexs = obj.get('indexs')
                            for ta in range(len(target_)):
                                temp = {}
                                if indexs is not None:
                                    keys = list(va.keys())
                                    target_l = target_[ta].xpath('./child::*')
                                    for k in range(len(keys)):
                                        t = self.getTrue(target_l, indexs[k]-1)
                                        if Util.isNull(t) is False:
                                            temp.setdefault(keys[k], t.xpath('string(.)').extract_first())
                                lis.append(temp)
                    return lis
                except Exception as e:
                    print('结果为list,type为list型:' + e)
        result = self.findTarget(node, obj, index)
        if result is not None:
            return result[0].xpath('string(.)').extract_first()
        return None

    def setModel(self,objs,response):
        content = response.xpath('//body')[0]
        for i in range(len(objs)):
            if type(objs[i].get('value')) == list:
                if objs[i].get('type') == 'list':
                    for l in range(len(objs[i].get('value'))):
                        keys = objs[i].get('value')[l].keys()
                        indexs = []
                        for key in keys:
                            result = content.xpath("//*[text()='" + objs[i].get('value')[l].get(key) + "']")
                            for re in result:
                                ancestor = self.getAncestor(re)
                                if len(ancestor) > 2:
                                    # 获取列表行的对应数据下标
                                    indexs.append(ancestor[-1].get('index'))
                                    objs[i].setdefault('ancestor', ancestor[:-2])
                            objs[i].setdefault('indexs', indexs)
                elif objs[i].get('type') == 'dict':
                    for l in range(len(objs[i].get('value'))):
                        result = content.xpath("//*[text()='" + objs[i].get('value')[l].get('value') + "']")
                        for re in result:
                            ancestor = self.getAncestor(re)
                            objs[i].get('value')[l].setdefault('ancestor', ancestor)
                            print(objs[i].get('value'))
            else:
                result = content.xpath("//*[text()='" + objs[i].get('value') + "']")
                for re in result:
                    ancestor = self.getAncestor(re)
                    objs[i].setdefault('ancestor', ancestor)
            #     数据为list时
        with open('bigData/data/models.txt', 'w+', encoding='utf-8') as fw:
            try:
                models = json.load(fw)
                models.append(objs)
                json.dump(models, fw)
            except Exception as e:
                models = []
                models.append(objs)
                json.dump(models, fw)
                print(e)
            fw.close()

    def getModels(self):

        if os.path.exists('bigData/data/models.txt') is False:
            return None
        with open('bigData/data/models.txt', 'r', encoding='utf-8') as fr:
            try:
                return json.load(fr)
            except Exception as e:
                print('......还未创建模型......')
                print(e)
            fr.close()
        return None

    def parse_one(self, response):
        # from scrapy.shell import inspect_response
        # inspect_response(response, self)
        # return
        url = response.url
        item = BigdataItem()
        item["url"] = url
        item["projectType"] = 'stockRights'
        item["source"] = "江苏产权交易所"
        item['obtainTime'] = str(datetime.datetime.now()).split(".")[0]
        transferRatio = None
        unionCode = None
        objs=[
            {"value":"江苏集萃药康生物科技有限公司3.72%股权（对应43.152万元出资额）",'key':'targetCompanyIndustry'},
            {"value": "17GQ20200030", 'key': 'id'},

             {"value": "江苏集萃药康生物科技有限公司", 'key': 'name'},

             {"value": [
                 {"name": "南京老岩企业管理中心（有限合伙）", 'rate': '65.96'}
             ], 'key': 'agency', 'type':'list'},
              {"value": [
                  {"value": "5429.27(收益法)", 'key': 'targetCompanyIndustry'},
                  {"value": "江苏省产业技术研究院有限公司", 'key': 'id'},
              ], 'key': 'ower', 'type': 'dict'}

        ]
        # /html/body[1]/div[@class="main"][2]/div[@class="text-container"][5]/div[@class="gpxx"][1]/div[@id="d-bdgk"]/table[@class="base-sw"][2]/tbody[1]/tr[1]/td[4]
        # print(response.xpath('/html[1]'))
        # return
        try:
            # 形成模型
            models = self.getModels()

            if models is None:
                self.setModel(objs,response)
            else:
                for model in models:
                    for obj in model:
                        item[obj.get('key')] = self.getTarget(response,obj)
            print(item)
        except Exception as e:
            print(e)
            print(item)
            file = codecs.open(self.filename, 'a', encoding='utf-8')
            file.write('Exception:' + str(e) + '   ')
            file.write('url:' + url + '\n')
            file.close()


    # 判断是否为数字
    def is_number(self, avgPrice):
        try:
            float(avgPrice)
            return True
        except ValueError:
            pass
        return False
