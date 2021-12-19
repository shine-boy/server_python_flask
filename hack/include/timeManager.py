# coding:utf-8
from hack.include import list as  my_list
from apscheduler.schedulers.background import BackgroundScheduler
import time
import threading
# 执行队列
class TimeManager:
    queues = []
    def __init__(self):
        self.sched = BackgroundScheduler()

    # 启动
    def run(self):
        self.sched.start()
        pass

    # 执行需要执行得方法
    def run(self, name, func, args):
        type = args['type']
        del args['type']
        @self.sched.scheduled_job(type, **args)
        def do_func():
            func()
            pass
        threading.Thread(target=do_func).start()
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
if __name__=='__main__':
    sched = BackgroundScheduler(timezone='MST')
    sched.add_job(job, 'interval', id='3_second_job', seconds=3)
    sched.start()
    sched.add_job(job4, 'interval', id='4_second_job', seconds=4)
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