# coding=utf-8
from flask import Response, Flask, request
from flask_cors import CORS
import json
from hack.include import Page
from hack.util import mongodb_connect
import traceback
class Request:
    def __init__(self, app: Flask):
        print('init')
        self.app = app
        pass

    def register(self, url, methods=['get']):
        def do(func):
            f = 'fd'
            CORS(self.app, resources=r"/*")

            @self.app.route( '/flask' + url, methods=methods, endpoint=func.__name__)
            def query():
                try:
                    data = self.get_date()
                    result = func(data)
                except Exception as e:
                    result = str(e)

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


class ServersApi:
    def __init__(self, app:Flask):
        self.request = Request(app)
        self.Page = Page
        self.myclient = mongodb_connect()
        pass




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
    # print(myclient.database_names())
    pass