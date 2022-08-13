# coding=utf-8
from hack.servers_api.serverApi import ServersApi
import datetime
from hack.util import isNull
from hack.include.threadManage import threadManage
from hack.stock import Statistic


class JournalApi(ServersApi):

    def __init__(self, app):
        ServersApi.__init__(self, app)
        self.threadManage = threadManage
        self.journal_db = self.myclient['journal']
        # 根据股票编号查询对应股票数据
        @self.register('/getjournal', methods=['POST', 'GET'])
        def getjournal(data):
            type = data.get('type')
            news = self.journal_db.get_collection('new')
            page = self.Page(data.get("page")).page
            sort = self.Sort({
                'order': data.get('order')
            }).sort
            query = {}
            lis = news.find(query).sort(sort).limit(page.get("pageSize")).skip(
                page.get("pageSize") * (page.get("current") - 1))
            lis = list(lis)
            for i in lis:
                print(i['time'], i['time'].timestamp())
                i['time'] = i['time'].timestamp() * 1000
                del i['_id']
            result = {
                'data': lis,
                'total': news.count_documents(filter=query)
            }
            return result