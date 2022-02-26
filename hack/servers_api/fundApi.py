# coding=utf-8
from hack.servers_api.serverApi import ServersApi


class FundApi(ServersApi):

    def __init__(self, app):
        ServersApi.__init__(self, app)

        @self.request.register('/getfund', methods=['POST', 'GET'])
        def getfund(data):
            page = self.Page(data.get("page")).page
            fund = self.myclient['stock_fund'].get_collection('fund')
            query = {}
            if data.get('code'):
                query['0'] = data.get('code')
            sortType = data.get("sort")
            if sortType is None:
                sort = [("date", -1)]
            else:
                sort = [(sortType, -1)]
            lis = fund.find(query, {"_id": 0}).sort(sort).limit(page.get("pageSize")).skip(
                page.get("pageSize") * (page.get("current") - 1))
            lis = list(lis)
            result = {
                'data': lis,
                'total': fund.count_documents(filter=query)
            }
            return result

