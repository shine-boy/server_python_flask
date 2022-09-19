# coding=utf-8
from flask import Response, Flask, request
from flask_cors import CORS
import os
import json
from hack.include import Page, Sort
from hack.util import mongodb_connect
from hack.journal import Journal
import traceback
class Request:
    def __init__(self, app: Flask):
        self.app = app
        self.journal = Journal(self)
        pass


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


class ServersApi(Request):
    def __init__(self, app:Flask):
        self.lastConnectTime = datetime.datetime.now()
        self.Page = Page
        self.myclient = mongodb_connect()
        self.Sort = Sort
        self.app = app
        self.journal = Journal(self)
        pass

    def re_connect(self):
        if datetime.datetime.now() - self.lastConnectTime > 10*1000*60:
            self.myclient = mongodb_connect()
            try:
                if self.myclient.database_names():
                    self.lastConnectTime = datetime.datetime.now()
            except Exception:
                print('reconnect')
                os.system("systemctl restart mongod")
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
                        print(result)
                        if result.find(':27017') > -1:
                            self.re_connect()
                        pass
                    # exc_type, exc_value, exc_traceback = sys.exc_info()
                    # result = str(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))  # 将异常信息转为字符串
                    self.journal.save(e, url )
                    pass
                return self.set_response(result)
        return do

    def set_response(self, result):
        response = Response()
        response.headers = {"Access-Control-Allow-Origin": "*"}
        response.data = json.dumps(result, cls=DateEncoder).encode('utf-8')
        return response

    def get_date(self):
        if request.method == 'POST':
            if request.data:
                data = json.loads(request.data)
            else:
                data = request.form
        else:
            data = request.args
        if request.files is not None and len(request.files) > 0:
            data['file'] = request.files['file']
        # if request.form is not None:
            # data['form'] = request.form.to_dict()

        return data

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
