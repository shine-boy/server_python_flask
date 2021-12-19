# coding=gbk
import json
import math
import os
import sys
import time
import time
import requests
import multiprocessing
import execjs
from urllib.parse import urlencode
import re
import shutil
import js2xml
from lxml import etree
class douyu:
    def __init__(self,query):
        self.query=query

        pass

    def loder(self,url):
        """直接请求ts文件的url然后在写入到本地"""
        html = requests.get(url).content
        l=url.find(".ts?")

        i = url[l-7:l]
        print(i)
        folder = "F:\movies\%s" % self.query["owner"]
        if os.path.isdir(folder) is False:
            os.system("md %s" % folder)
        with open(r"%s\%07s.ts" % (folder, i), "wb") as f:
            f.write(html)

    def ts_to_mp4(self):
        print('ts文件正在进行转录mp4......')
        folder="F:\movies\%s" % self.query["owner"]

        str = "cd /d %s\\ && copy /b *.ts %s.mp4"%(folder,self.query["title"])  # copy /b 命令
        print(str)
        os.system(str)
        filename = folder+"\/"+ self.query["title"] + '.mp4'
        if os.path.isfile(filename):
            te = "del %s\\*.ts"%folder
            print(te)
            os.system(te)
            print('转换完成，祝你观影愉快')

        # shutil.rmtree("test")

    def get_js(self):
        f = open(".\key.js", 'r', encoding='UTF-8')
        line = f.readline()
        htmlstr = ''
        while line:
            htmlstr = htmlstr + line
            line = f.readline()
        return htmlstr


    def run(self):
        dom = requests.get(self.query["url"])
        dom = etree.HTML(dom.content)

        jstext="var CryptoJS = require('crypto-js');"+dom.xpath("//script")[2].text
        ub98484234 = execjs.compile(jstext)
        data = ub98484234.call('ub98484234', self.query["vid"], "10000000000000000000000000001501", int(time.time()))
        data = data + "&vid=" + self.query["hashId"]
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        print(data)
        res = requests.post("https://v.douyu.com/api/stream/getStreamUrl", data=data, headers=headers)
        print(res.json())
        list = res.json()["data"]["thumb_video"]["high"]["url"]
        tss = requests.get(list)

        url = list[:list.find("playlist.m3u8")]
        lis = [url + x for x in tss.text.split("\n") if x != "" and x[0] != "#"]
        pool = multiprocessing.Pool(processes=3)
        pool.map(self.loder, lis)
        pool.close()
        pool.join()
        self.ts_to_mp4()

if __name__ == "__main__":
    query = {
        "kw": 7302297,
        "page": 1,
        "pageSize": 20,
        "filterType": 0,
        "tabType": 1

    }
    res = requests.get("https://www.douyu.com/japi/search/api/searchVideo?" + urlencode(query))
    total = res.json()["data"]["total"]
    lists = []
    for i in range(1, math.ceil(total / 20) + 1):
        query["page"] = i
        print("current "+str(i))
        res = requests.get("https://www.douyu.com/japi/search/api/searchVideo?" + urlencode(query))
        videos = res.json()["data"]["relateVideo"]
        lists.append(videos)
        print(len(videos))
        for v in range(len(videos)):
            temp = videos[v]
            temp["owner"] = "V" + temp["owner"]
            temp["title"] = temp["title"].replace(" ", ".").replace(":", ".")+"-"+temp["hashId"]

            url = temp["url"]
            folder = "F:\movies\%s" % temp["owner"]
            filename = folder + "\/" + temp["title"] + '.mp4'
            print(filename)
            if os.path.isfile(filename):
                print(temp["title"] + '.mp4' + "已存在")
                continue
            dou = douyu(temp)
            dou.run()
    f=open("F:\movies\catalogue.json", 'w', encoding='utf-8')
    json.dump(lists, f)





