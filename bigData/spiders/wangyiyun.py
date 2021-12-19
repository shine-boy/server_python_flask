
import scrapy
from bigData.spiders.run import WanYiYun ,set_user_agent
import json
from bigData.items import BigdataItem
import requests
class wangyiyun(scrapy.Spider):
    name='wangyiyun'

    def __init__(self):

        pass

    def start_requests(self):
        types=[
            {
            'id':"2250011882",
            'type':"抖音排行榜"
            },
            {
                'id': "19723756",
                'type': "云音乐飙升榜"
            },
            {
                'id': "3778678",
                'type': "云音乐热歌榜"
            },]
        # type=types[0]
        print('start')
        for type in types:
            url = 'https://music.163.com/discover/toplist?id='+type["id"]
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse,meta={"type":type["type"]})

    def parse(self, response):
        lis = json.loads(response.xpath('//textarea[@id="song-list-pre-data"]').xpath("string(.)").extract_first())
        url='https://music.163.com/#'
        for li in lis:
            artists=li['artists']
            name=li["name"]
            id=li["id"]
            type=response.meta['type']
            ref=url+"/song?id="+str(id)
            yield scrapy.Request(url=ref, dont_filter=True, callback=self.parse_song,meta={"name":name,"artists":artists,'type':type})

    def parse_song(self,response):
        wanyiyun = WanYiYun()
        # print(response.request.url.split("="))
        # print(wanyiyun.get_encSecKey())
        # print("085129a64df4a3765d751725ff686687da85b83acde042a9ec7f3da22d7430c1a5801b25675813bc17660001d943ce77a66832f57ea4377fec0c7c52a684d3f2f4d67ccd38181131b1351abc5860ec09610dc27a7308a2ac7f5578475e5350d37a80f00516f29aa173c08f24ba9e10ac8b4c115002f9c0adb128d306b202cf6f")
        # print(wanyiyun.get_params(response.request.url.split("=")[1]))
        # print(
        #     "4eJRRPV3wPBi2C7TVviqNfWsyDzNM9MTbBbfalBJXdT0+KmVukjbp20pNYOFk9b+R67oEb+OeyrCiRrR4NnjXv2yoYw3RX/dMybRFBQTlSYN7/GJ3nvOMyy7heISa88MiFv/L1gfbRBicIMn1zRDwYdgeB+QVHkTqoqyM1MnkkgHyjoZCo4Jayf98U9CFtANlEGWz6Utn+fiXq0nyRZDQupTPsFYNiE4iwP1WFvvKUXLiO+h+mFBTzn8lu8YWWh5eHxyfyz560+ZHnBruRvpUZ6tOkwVF1p5TsQwSKmaOr0=")

        data={
                                 "params":wanyiyun.get_params(response.request.url.split("=")[1]),
                                 "encSecKey":wanyiyun.get_encSecKey()
                             }
        res=requests.post("https://music.163.com/weapi/comment/resource/comments/get?csrf_token=",data=data,headers = {
                                    "referer":response.request.url,
                                    "origin":response.request.url.split("?")[0],
                                    "content-type":"application/x-www-form-urlencoded",
                                    "user-agent":set_user_agent()
                                })

        data=res.json().get("data")
        # print(data.get("hotComments"))
        items=BigdataItem()
        items['type']=response.meta['type']
        items["name"]=response.meta["name"]
        items["artists"] = response.meta["artists"]
        items["id"]=response.request.url.split("=")[1]
        items["url"]=response.request.url
        items["totalCount"] = data.get("totalCount")
        items["comments"]=data.get("hotComments")
        yield items
        # print(res.request)
        # print(res)
        # print(res.text)
        # print(res.json())
        # print(res.content)
        # yield scrapy.Request(url="https://music.163.com/weapi/comment/resource/comments/get?csrf_token=", dont_filter=True, callback=self.tesat,
        #                      method="POST",
        #                     headers={
        #                         "referer":response.request.url,
        #                         "origin":response.request.url.split("?")[0],
        #                         "content-type":"application/x-www-form-urlencoded",
        #                         "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.183 Safari/537.36 Edg/86.0.622.63"
        #                     },
        #                      body=json.dumps({
        #                          "params":wanyiyun.get_params(response.request.url.split("=")[1]),
        #                          "encSecKey":wanyiyun.get_encSecKey()
        #                      })
        #                     )
        # print(response.text)

    def tesat(self,response):
        print(response.request.headers)

        print(response.text)
