# coding=utf-8
from lxml import etree
import re
import pymongo
anstype=["A","B","C","D","E","F","G","H","I","J"]
# 过滤无效字符
def filter_null(s,type=None):
    if isinstance(s,str):
        s=re.sub(r"[\t\n\r\xa0]*","",s)
        try:
            if type is not None and type != '':
                if type == "type":
                    if s.find("题目解析")>-1:
                        s = re.split("[:：]", s)[1]
                    elif len(re.compile("此题.*分,得.*分").findall(s))>0:
                        s=""
                elif type=="ans":
                    if s.find("参考答案")>-1:
                        s = re.split("[:：]", s)[1]
                elif type=='content':
                    s = re.sub(r"^[\d]*[、]", "", s)
                elif anstype.index(type)>-1:
                    s = re.sub(r"^[ABCDEFGHIJ][、.]", "", s)

        except Exception as e:
            print(e)
        s = s.strip()
    return s

# 判断是否插入数据库
def insertFlag(obj,db,keys=["content","type","ans","A","B","C","D"]):
    if obj.get("ans") is None or obj.get("ans") == '':
        raise Exception("ans 不能为空")
    if db is None:
        return True
    for key in keys:
        if obj.get(key)!=db.get(key):
            return True
    return False

# 舍弃的部分，去除不规则的数据
def dropFlag(st):
    if re.sub("^(\d+|[ABCDEFGHIJ])[、.]","",st) =="":
        return True
    # pater=re.compile("\d+[、]")
    # result=pater.match(st)
    # if result is not None:
    #     return True
    return False


def update_mongo(result,mydb):
    def delete_one(collection,obj,keys=["content","A","B","C","D"]):
        query={}
        for key in keys:
            if obj.get(key) is not None:
                query[key]=obj.get(key)
        collection.delete_one(query)
        pass
    choice = mydb["choice"]
    multiSelect = mydb["multiSelect"]
    for ty in result:
        if ty["title"].startswith("单选"):
            for li in ty["list"]:
                delete_one(choice,li)
                choice.insert_one(li)
        elif ty["title"].startswith("多选"):
            for li in ty["list"]:
                delete_one(multiSelect, li)
                multiSelect.insert_one(li)

# 插入数据库，存在则忽略
def insert_mongo(result,mydb):
    choice = mydb["choice"]
    multiSelect = mydb["multiSelect"]
    for ty in result:
        if ty["title"].startswith("单选"):
            for li in ty["list"]:
                if insertFlag(li,choice.find_one({'content':li["content"]})):
                    choice.insert_one(li)
        elif ty["title"].startswith("多选"):
            for li in ty["list"]:
                if insertFlag(li,multiSelect.find_one({'content':li["content"]})):
                    multiSelect.insert_one(li)

# xpath列表获取其内容文本
def string_(lis):
    result=''
    for li in lis:
        result+=li.xpath("string(.)")
    return result



def htmlTo_mongo(path,mydb):
    html=etree.parse(path,parser=etree.HTMLParser(encoding='GBK'))

    types=html.xpath("//div[@id='con_xz_1']")
    result=[]

    for t in types:
        obj={}
        obj['title']=filter_null(t.xpath("div/div[1]")[0].xpath("string(.)"))
        lis=t.xpath("ul/descendant::tr/td[1]")

        temp=[]
        for li in lis:
            o={}
            print(string_(li.xpath("div[1]/p")))
            o['content']=filter_null(string_(li.xpath("div[1]/p")),'content')
            if dropFlag(o['content']):
                continue
            ans=li.xpath("div[1]/div[@class='f_l']/p")
            anst=0
            ans_=''
            for i in range(len(ans)):
                ans_+=filter_null(ans[i].xpath("string(.)"),anstype[anst])
                print(ans_)
                if dropFlag(ans_) is False:
                    o[anstype[anst]]=ans_
                    anst+=1
                    ans_=''

            o["ans"]=filter_null(li.xpath("p[1]")[0].xpath("string(.)"),'ans')
            o["type"]=filter_null(li.xpath("p[2]")[0].xpath("string(.)"),'type')
            temp.append(o)
        obj["list"]=temp
        result.append(obj)
    # for ti in result:
    #     print(ti['title'])
    #     for li in ti['list']:
    #         print(li)
    print(len(result))
    print(len(result[0]['list']))
    print(len(result[1]['list']))
    insert_mongo(result,mydb)

# 清洗数据
def filter_mongo(mydb,collections=["choice","multiSelect"]):
    for type in collections:
        collection=mydb[type]
        lis=collection.find()
        for li in lis:
            for key in li:
                li[key]=filter_null(li[key],key)
            if li.get("ans") is None or li.get("ans")=='':
                raise Exception("ans 不能为空")
            collection.delete_one({"_id":li["_id"]})
            collection.insert_one(li)

if __name__ == "__main__":
    myclient = pymongo.MongoClient("mongodb://192.168.142.1:27017/")
    mydb = myclient["projectExam"]
    # choice = mydb["choice"]
    htmlTo_mongo("C:\\Users\liu_hfei\Desktop\\" + 'base64.txt', mydb)
    # with open("C:\\Users\liu_hfei\Desktop\\base64.txt",'r',encoding='GBK') as f:
    #     print(f.read())
    # paths=["test.html","CVICSE E-Learning系统.html","项目经理考试页面.htm"]
    # for parh in paths:
    #     htmlTo_mongo("C:\\Users\liu_hfei\Desktop\\"+parh,mydb)
    # filter_mongo(mydb)
    # choice = mydb["choice"]
    # print(choice.estimated_document_count())

    from datetime import datetime


    # print(datetime.now().isoweekday())
    pass