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
                    sort = [("date", -1)]
                else:
                    sort = [(sortType, -1)]
                lis = fund.find(query, {"_id": 0}).sort(sort).limit(page.get("pageSize")).skip(
                    page.get("pageSize") * (page.get("current") - 1))
                lis = list(lis)
                for i in lis:
                    i['time'] = i['time'].timestamp()
                result = {
                    'data': lis,
                    'total': fund.count_documents(filter=query)
                }
                print(result)
                return result
            else:
                return '未查询到数据'

