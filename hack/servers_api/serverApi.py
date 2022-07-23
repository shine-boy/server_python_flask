# coding=utf-8
from flask import Response, Flask, request
from flask_cors import CORS
import json
from hack.include import Page
from hack.util import mongodb_connect
import traceback
class Request:
    def __init__(self, app: Flask):
        self.app = app
        pass

    def register(self, url, methods=['get']):
        def do(func):
            CORS(self.app, resources=r"/*")

            @self.app.route( '/flask' + url, methods=methods, endpoint=func.__name__)
            def query():
                try:
                    data = self.get_date()
                    result = func(data)
                except Exception as e:
                    result = str(e)
                    if self.myclient:
                        #  mongo连接失败重连
                        if result.index(':27017') > -1:
                            self.re_connect()
                        pass
                    # exc_type, exc_value, exc_traceback = sys.exc_info()
                    # result = str(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))  # 将异常信息转为字符串
                    print(result)
                    pass
                return self.set_response(result)
        return do

    def set_response(self, result):
        response = Response()
        response.headers = {"Access-Control-Allow-Origin": "*"}
        response.data = json.dumps(result).encode('utf-8')
        return response

    def get_date(self):
        if request.method == 'POST':
            if request.data:
                data = json.loads(request.data)
            else:
                data = request.form
        else:
            data = request.args
        return data


class ServersApi(Request):
    def __init__(self, app:Flask):
        self.lastConnectTime = datetime.datetime.now()
        Request.__init__(self, app)
        self.Page = Page
        self.myclient = mongodb_connect()

        pass

    def re_connect(self):
        if datetime.datetime.now() - self.lastConnectTime > 10*1000*60:
            self.myclient = mongodb_connect()
    # def __get__(self, instance, owner):
    #     print(instance, owner, 'gfgfgf')


def test(f):
    # print(re)
    print('servers_api')

    f('df')

@test
# lambda f: print('1')
def g(h):
    print('1')

import sys
import datetime
if __name__ == '__main__':
    # f = lambda r:1+1,print('fd')
    fd='111111111'
    test.__name__ = 'test1'
    print(test.__name__)
    print("fsfs%s"%fd)
    print(datetime.datetime.now().timestamp())
    s = ServersApi('')
    print(s.myclient.database_names())
    print('address',s.myclient.address)

    # print(myclient.database_names())
    pass