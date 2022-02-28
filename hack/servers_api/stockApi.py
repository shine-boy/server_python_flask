# coding=utf-8
from hack.servers_api.serverApi import ServersApi


class StockApi(ServersApi):

    def __init__(self, app):
        ServersApi.__init__(self, app)

        @self.request.register('/getstock', methods=['POST', 'GET'])
        def getstock(data):
            if data.get('code'):
                code = data.get('code')
                fund = self.myclient['dongfangcaifu'].get_collection(code)
                page = self.Page(data.get("page")).page
                query = {}
                sortType = data.get("sort")
                if sortType is None:
                    sort = [("time", -1)]
                else:
                    sort = [(sortType, -1)]
                lis = fund.find(query).sort(sort).limit(page.get("pageSize")).skip(
                    page.get("pageSize") * (page.get("current") - 1))
                lis = list(lis)
                for i in lis:
                    print(i['time'], i['time'].timestamp())
                    i['time'] = i['time'].timestamp() * 1000
                    i['_id'] = str(i['_id'])
                result = {
                    'data': lis,
                    'total': fund.count_documents(filter=query)
                }
                print(result)
                return result
            else:
                return '未查询到数据'

        @self.request.register('/getnames', methods=['POST', 'GET'])
        def getnames(data):
            fund = self.myclient['dongfangcaifu'].get_collection('names')
            page = self.Page(data.get("page")).page
            query = {}
            if data.get('search'):
                query['$or'] = [{ 'name': {'$regex': data.get('search')}}, { 'code': {'$regex': data.get('search')}}]
            lis = fund.find(query).limit(page.get("pageSize")).skip(
                page.get("pageSize") * (page.get("current") - 1))
            lis = list(lis)
            for i in lis:
                i['_id'] = str(i['_id'])
            result = {
                'data': lis,
                'total': fund.count_documents(filter=query)
            }
            return result
