
import scrapy
import json
import re
from scrapy.utils.project import get_project_settings
from bigData.items import BigdataItem
class demo(scrapy.Spider):
    name="shanghai"

    def __init__(self):
        # 代理配置
        settings = get_project_settings()
        self.post={
            "projectType":"CHANQUAN",
            "gplx":"2",
            "isGw":True,
            "xmbh":"",
            "xmmc":"",
            "szdqs":"",
            "pageQuery":{"pageIndex":1,"pageSize":20}
        }
        self.headers = {
            "Content-Type":"application/json;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
        }
        pass

    # 上海产权交易所股权
    def start_requests(self):
        url = 'https://www.suaee.com/manageprojectweb/foreign/project/queryAllNew'

        yield scrapy.Request(url=url, dont_filter=True, callback=self.parse,headers=self.headers,
                             meta={"handle_httpstatus_all": True},
                             method='POST',body=json.dumps(self.post),errback=self.parse)

    def parse(self, response):

        data=json.loads(response.text)
        pageCount=data["data"]["pageCount"]
        for da in data["data"]["data"]:
            item = BigdataItem()
            item["province"]=da.get("szdqs")
            item["city"] = da.get("szdqsq")
            item["region"] = da.get("szdqqx")
            item["name"] = da["xmmc"]
            item["floorPrice"] = da["zrdj"]
            xmid=da["xmid"]
            nextUrl="https://www.suaee.com/manageproject/foreign/projectPreview/getCQProjectPreview?xmid="+str(xmid)+"&gplx=&type=&imgType="
            yield scrapy.Request(url=nextUrl, dont_filter=True, callback=self.parsePage, headers=self.headers,
                                 meta={"item": item},
                                 )
        if self.post["pageQuery"]["pageIndex"]==1:
            for page in range(1,pageCount):
                self.post["pageQuery"]["pageIndex"]=page+1
                url = 'https://www.suaee.com/manageprojectweb/foreign/project/queryAllNew'
                yield scrapy.Request(url=url, dont_filter=True, callback=self.parse, headers=self.headers,
                                     meta={"handle_httpstatus_all": True},
                                     method='POST', body=json.dumps(self.post))
        pass

    def parsePage(self,response):
        pass
        item=response.meta["item"]
        try:
            data=json.loads(response.text)["data"]
            item["type"]=data.get("sshy")
            item["source"] = "上海联合产权交易所"
            yield item
        except Exception as e:
            print(e)
            print("项目不存在")
