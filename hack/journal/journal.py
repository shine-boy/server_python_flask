# coding=utf-8
from hack.util import mongodb_connect
import datetime
class Journal:
    def __init__(self, name: str or object = ''):
        self.journal_db = mongodb_connect()['journal']
        if type(name) != str:
            self.name = name.__str__().split(' ').pop(0).replace('<', '').split('.').pop()
        else:
            self.name = name
        pass

    def save(self, error: Exception, description:str = 'error', type='error'):
        error_message = str(error)
        result = {
            'type': type,
            'time': datetime.datetime.now(),
            'message': error_message,
            'name': self.name,
            "key": description,
            "description": description
        }
        self.journal_db['new'].insert_one(result)
        # exc_type, exc_value, exc_traceback = sys.exc_info()
        # result = str(repr(traceback.format_exception(exc_type, exc_value, exc_traceback)))  # 将异常信息转为字符串

if __name__ == '__main__':
    print('ffd{}'.format(1))