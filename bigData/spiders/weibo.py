import scrapy
from scrapy.http.cookies import CookieJar
class demo(scrapy.Spider):
    name="weibo"
    domain=".weibo.com"
    def __init__(self):
        # 代理配置
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36"
        }
        pass

    # 上海产权交易所股权
    def start_requests(self):
        url = 'https://weibo.com'

        yield scrapy.Request(url=url, dont_filter=True, callback=self.getTarget,headers=self.headers,
                             meta={"handle_httpstatus_all": True},
                             method='GET')

    def getTarget(self,response):
        print(response.request.headers)
        cookie_jar = CookieJar()
        cookie_jar.extract_cookies(response, response.request)
        print(cookie_jar) 
        cookie_dict = dict()
        cookie_list =''
        for k, v in cookie_jar._cookies.items():
            for i, j in v.items():
                for m, n in j.items():
                    cookie_dict[m] = n.value
        for i,j in cookie_dict.items():
            print(i,'----------------',j)
        # url = "https:"+response.xpath('//div[@id="pl_feedlist_index"]/descendant::a[1]/@href').extract_first()
        # print(url)
        # yield scrapy.Request(url=url, dont_filter=True, callback=self.parse,
        #                      meta={"handle_httpstatus_all": True,'cookiejar': cookie_jar},
        #                      method='GET',errback=self.parse)

    def parse(self,response):
        if 'location' in  response.headers:
            url =  response.headers['location'].decode()
            print(url)
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse,headers=self.headers,
                                meta={"handle_httpstatus_all": True},
                                method='GET')
        else:
            print(response.text)
    