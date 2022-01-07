# coding:utf-8
from apscheduler.schedulers.background import BackgroundScheduler
import time
import os
import threading
# 执行队列
class TimeManager:
    queues = []
    def __init__(self):
        self.sched = BackgroundScheduler()
        self.sched.start()

    # 执行需要执行得方法
    def run(self, name, func, args):
        type = args['type']
        del args['type']
        @self.sched.scheduled_job(type, **args, id=name)
        def do_func():
            func()
            pass
        # threading.Thread(target=do_func).start()
        pass

    def find_queue_index(self, name):
        for i in range(self.queues):
            if self.queues[i]['name'] == name:
                return i
        return None

    # 关闭
    def shut(self, name):
        index = self.find_queue_index(name)
        if index:
            self.queues.pop(index)

    # 激活
    def activate(self, name, do):
        self.queues.append({
            'name': name,
            'do': do
        })
        self.run(name)

    def stop(self):
        pass

def test(*args,**kwargs):
    def test1(name,g):
        print(name)
        print(g)
    test1(**kwargs)

def job():
    print('job 3s')

def job4():
    print('job 4s')

import datetime
if __name__=='__main__':
    timeManager = TimeManager()
    timeManager.run('test',job,{
        'seconds': 3,
        'hours': 1,
        'type': 'interval'
    })
    timeManager.run('test4', job4, {
        'seconds': 4,
        'hours': 1,
        'type': 'interval',
        'start_date': datetime.datetime(2021, 2, 2, 18, 0, 0)
    })

    # sched = BackgroundScheduler(timezone='MST')
    # sched.add_job(job, 'interval', id='3_second_job', seconds=3)
    # sched.start()
    # sched.add_job(job4, 'interval', id='4_second_job', seconds=4)
    # print(os.path.dirname(os.path.abspath(__file__)))
    while (True):
        print('main 1s')
        time.sleep(1)

# if __name__ == '__main__':
#     print(my_list.findIndex([1],1))
#     t = [{'name':'1'},{'name':2}]
#     t.pop(0)
#     obj={
#         'name':'fd',
#         'g':'sd'
#     }
#     test(**obj)
#     print(t)