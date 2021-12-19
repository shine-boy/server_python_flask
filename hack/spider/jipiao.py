
import requests
import json
from datetime import datetime,date
import calendar
import math
from  hack.util import MyIterator,getKeys_dic


class Jipiao:

    def to_time(self,now):
        if now is None:
            now=datetime.now()
        if type(now) is str:
            try:
                now=datetime.fromisoformat(now)

            except ValueError as v:
                print(v+":输入时间格式错误，默认使用当前时间")
                now = datetime.now()
        return now

    def qunaLvXing(self,start="上海",end="昆明",now=None):
        now=self.to_time(now)

        params={
                   'apiHost': 'lp',
                   'apiPath': '/api/lp_multifetch',
        'apiMethod': 'POST',
        'apiDataType': 'json',
        'apiKey': 'get_lowest_price',
        'apiData[data]': '["%s,%s,%d-%02d-%02d,,false"]'%(start,end,now.year,now.month,now.day)
        }
        headers={
            'origin': 'https://flight.qunar.com',
            'content-type': 'application/x-www-form-urlencoded'
        }
        res=requests.post(url="https://flight.qunar.com/f_fe/lp",data=params,headers=headers)
        data=json.loads(res.text)
        if data['ret'] is True:
            return data.get('data')[0]
        return None

    def getXieChengCity(self):
        url="https://flights.ctrip.com/itinerary/api/poi/get?v=0.05566237655802997"
        res=requests.get(url)
        data=json.loads(res.text)
        result=[]
        if data.get("msg") == 'success':
            data=data.get('data')
            for i in data:
                if type(data[i]) is dict :
                    for ke in data[i]:
                        result.extend(data[i][ke])

        return result

    def xiuCheng(self,start="上海",end="昆明",now=None,citys=None):

        if citys is None:
            citys=self.getXieChengCity()
        for city in citys:
            if start.find(city.get("display"))>-1:
                start=city.get("data").split("|")[-1]
            if end.find(city.get("display"))>-1:
                end=city.get("data").split("|")[-1]
        url="https://flights.ctrip.com/international/search/api/lowprice/calendar/getCalendarDetailList?v=0.895018031816839"
        now=self.to_time(now)
        params={
           'cabin': "Y_S_C_F",
            'flightSegmentList': [{'arrivalCityCode': end, 'departureCityCode': start, 'departureDate': now.strftime("%Y-%m-%d")}],
           'flightWay': "S"
        }
        headers={
            # 'content-length': '138',
            # 'pragma': 'no-cache',
            # 'sec-fetch-dest': 'empty',
            # 'sec-fetch-mode': 'cors',
            'scope': 'd',#不可缺
            'sec-fetch-site': 'same-origin',
            'accept': 'application/json',
            'accept-language':'zh-CN,zh;q=0.9,en;q=0.8',
            'transactionid': '64c617b6ff1a4897aac49cc830fb8018',
            'origin': 'https://flights.ctrip.com',
            'user-agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
            'content-type': 'application/json;charset=UTF-8',
            # 'cookie':'_ga=GA1.2.417215948.1610520078; _gid=GA1.2.1681916402.1610520078; Union=OUID=&AllianceID=4897&SID=799897&SourceID=&createtime=1610520083&Expires=1611124882709; MKT_OrderClick=ASID=4897799897&AID=4897&CSID=799897&OUID=&CT=1610520082724&CURL=https%3A%2F%2Fflights.ctrip.com%2Finternational%2Fsearch%2Fdomestic%3Fallianceid%3D4897%26sid%3D799897%26utm_medium%3Dbaidu%26utm_campaign%3Durldx%26utm_source%3Dbaiduppc%26url_targeting%3D1%26bd_vid%3D11504762106639234475&VAL={"pc_vid":"1610520073249.pnmd8"}; MKT_Pagesource=PC; appFloatCnt=1; _bfi=p1%3D101023%26p2%3D0%26v1%3D1%26v2%3D0; MKT_CKID=1610520116669.p55km.55tl; MKT_CKID_LMT=1610520116678; _RF1=153.37.190.166; _RSG=C44BWFpxbTDol1F1Qk1GZ9; _RDG=28b8255ae614e92b2908ace65198dbd5d5; _RGUID=d765ef33-e02c-410c-98d0-06e6813c1bf2; __zpspc=9.1.1610520116.1610520121.2%231%7Cbaiduppc%7Cbaidu%7Curldx%7C%7C%23; _jzqco=%7C%7C%7C%7C1610520122463%7C1.2092067306.1610520116662.1610520116662.1610520122107.1610520116662.1610520122107.undefined.0.0.2.2; _abtest_userid=804ea124-f537-464e-9add-be8a1b666308; FlightIntl=Search=[%22HGH|%E6%9D%AD%E5%B7%9E(HGH)|17|HGH|480%22%2C%22KMG|%E6%98%86%E6%98%8E(KMG)|34|KMG|480%22%2C%222021-01-14%22]; _bfa=1.1610520073249.pnmd8.1.1610520073249.1610520073249.1.2; _bfs=1.2',
            'referer':'https://flights.ctrip.com/international/search/oneway-hgh-kmg?depdate=2021-01-14&cabin=Y_S_C_F'
        }
        res=requests.post(url=url,data=json.dumps(params),headers=headers)
        data=json.loads(res.text)
        if data.get("msg") == 'success':
            return data.get('data')
        return None


    def getJiPiao(self,start=['上海','杭州','无锡','南通','南京','常州'],
                     end="昆明",now=None,do=None,keys=['dep','arr','depDate','price','flightNO'],**kwargs):
        if do is None:
            do=self.qunaLvXing
        result = []
        for s in start:

            data = do(start=s, end=end, now=now,**kwargs)
            if data is not None:
                if keys is not None and len(keys) >0 :
                    data=getKeys_dic(data,keys)
                result.append(data)
        return result

    def formateTimes(self,times):

        for i in range(len(times)):
            if type(times[i]) is str:
                try:
                    times[i]= datetime.fromisoformat(times[i])
                except ValueError as v:
                    print(v + ":输入时间格式错误")
                    times=[]
        return times


    def getTimes(self,start,l):
        start= self.to_time(start)
        year = start.year
        month = start.month
        monthlen = calendar._monthlen(year, month)
        for i in range(l):
            day = (start.day + i)
            if day > monthlen:
                day = day - monthlen
                month += 1
            if month > 12:
                month = month - 12
                year += 1
            yield datetime(year=year,month=month,day=day)

    def getJiPiaos(self,times=[],space=['2021-02-08', '2021-02-11'],after=[],**kwargs):
        times=self.formateTimes(times)
        space=self.formateTimes(space)
        myIteratar=MyIterator(times)
        result=[]

        if len(space)==2 and space[1]>space[0]:
            myIteratar.append(self.getTimes(space[0],math.floor((space[1].timestamp()-space[0].timestamp())/(3600*24))))

        if len(after)>1:
            after[0]=self.formateTimes([after[0]])[0]
            if len(after)==1:
                after.append(1)
            myIteratar.append(self.getTimes(after[0], after[1]))

        for ti in myIteratar:
            result.append(self.getJiPiao(now=ti,**kwargs))
        return result

    def getMin(self):

        citys = self.getXieChengCity()
        result = []
        min = 10000
        temp = {}
        for i in self.getJiPiao(keys=None, do=self.xiuCheng, citys=citys):
            for ti in self.getTimes("2021-02-07", 3):
                for n in i:

                    if ti == datetime.fromisoformat(n.get("departureDate")):
                        result.append(n)

        for re in result:
            if re.get('price') < min:
                min = re.get('price')
                temp = re
        for ci in citys:
            if ci['data'].find(temp['departureCityCode']) > -1:
                temp['departureCityCode'] = ci['display']
            if ci['data'].find(temp['arrivalCityCode']) > -1:
                temp['arrivalCityCode'] = ci['display']
        minPrice={
            '携程':temp
        }


        result = self.getJiPiaos()
        min = 10000
        temp_ = {}
        for i in result:
            for j in i:
                if j['price'] < min:
                    min = j['price']
                    temp_ = j
        minPrice['去哪旅行']=temp_
        return minPrice

