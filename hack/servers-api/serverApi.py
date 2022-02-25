from flask import Response, Flask, request, make_response
from flask_cors import CORS
import json

app = Flask(__name__)


class Request:
    def __init__(self, url, methods=['get']):
        print('init')
        self.url = url
        self.methods = methods
        pass

    def __call__(self, func):

        CORS(app, resources=r"/*")

        @app.route(self.url, methods=self.methods)
        def query():
            print('start')
            data = self.get_date()
            result = func(data)
            print('end')
            return self.set_response(result)

    @staticmethod
    def set_response(self, result):
        response = Response()
        response.headers = {"Access-Control-Allow-Origin": "*"}
        response.data = json.dumps(result)
        return response

    @staticmethod
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
    def __init__(self):
        pass


def test():
    print('test')


# @test
def g():
    print('1')


if __name__ == '__main__':
    g()
