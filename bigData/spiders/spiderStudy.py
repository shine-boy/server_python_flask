
import scrapy
import json
import re
from scrapy.utils.project import get_project_settings
from bigData.items import BigdataItem
class demo(scrapy.Spider):
    name="demo"

    def __init__(self):
        # 代理配置
        settings = get_project_settings()

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
        }
        pass

    def start_requests(self):
        url = 'http://www.jscq.com.cn/dsf/gq/jygg/index.html'

        yield scrapy.Request(url=url, dont_filter=True, callback=self.parse)

    def parse(self, response):
        totalPage=response.xpath('//a[@id="pagenav_tail"]/@href').extract_first().strip()
        totalPage=re.search("(?<=_)\d*?(?=\.)",totalPage).group()

        # print(re.search("(?<=_)\d*?(?=\.)",totalPage).group())
        for i in range( -1,int(totalPage)):
            if i==-1:
                url = 'http://www.jscq.com.cn/dsf/gq/jygg/index.html'
            else:
                url = 'http://www.jscq.com.cn/dsf/gq/jygg/index_'+str(i+1)+".html"

            yield scrapy.Request(url=url, dont_filter=True, callback=self.parsePage,headers=self.headers,

                                 )

    def parsePage(self,response):
        item = BigdataItem()
        res = response.xpath('//table/tr[@style="height:36px;"]')
        for r in res:
            td=r.xpath("td")
            item["name"]=td[1].xpath('./a/@title').extract_first().strip()
            item["floorPrice"] = td[3].xpath("string(.)").extract_first().strip()
            item["type"] = td[2].xpath("string(.)").extract_first().strip()
            yield item
        # print(item)
        # print(res)
