# coding=utf-8
from hack.servers_api.serverApi import ServersApi
import datetime

import hack.include.excel as myExcel
from hack.util import isNull
from hack.include.threadManage import threadManage


class OtherApi(ServersApi):

    def __init__(self, app):
        ServersApi.__init__(self, app)
        self.threadManage = threadManage

        @self.register('/wangyiyun', methods=['POST', 'GET'])
        def getwangyiyun(data):
            page = self.Page(data.get("page")).page
            sort = self.Sort({
                'order': data.get('order'),
                'sort': data.get("sort")
            }).sort
            comments = self.myclient['local']["comments"]
            query = {"comments.likedCount": {"$gt": 2}}
            lis = comments.find(query, {"_id": 0}).sort(sort).limit(page.get("pageSize")).skip(
                page.get("pageSize") * (page.get("current") - 1))
            lis = list(lis)
            #
            result = {
                'data': lis,
                'total': comments.estimated_document_count()
            }
            return result

        @self.register('/deleteWangyiyun', methods=['POST', 'GET'])
        def deleteWangyiyun(data):
            comments = self.myclient['local']["comments"]
            query = {'id': data["id"]}
            comments.delete_one(query)
            return True

        @self.register('/projectExam', methods=['POST', 'GET'])
        def seachprojectExam(data):
            page = self.Page(data.get("page")).page
            type_ = data.get("questionType", "choice")
            comments = self.myclient['projectExam'][type_]
            query = {}
            if isNull(data.get("content")) is False:
                query['content'] = {'$regex': ".*" + data.get("content") + ".*"}
            if isNull(data.get("type")) is False:
                query['type'] = {'$regex': ".*" + data.get("type") + ".*"}
            lis = comments.find(query, {"_id": 0}).limit(page.get("pageSize")).skip(
                page.get("pageSize") * (page.get("current") - 1))
            lis = list(lis)
            #
            result = {
                'data': lis,
                'total': comments.estimated_document_count()
            }
            return result

        @self.register('/uploadProjectExel', methods=['POST', 'GET'])
        def uploadProjectExel(data, my_file):
            try:
                data = data['form']

                if data and data.get('type') == '1':
                    resfile = myExcel.jibing(my_file, head=data.get('header'), filter=data.get('filter'))
                else:
                    resfile = myExcel.waike(my_file, head=data.get('header'), filter=data.get('filter'))
            except Exception as e:
                pass

            return resfile