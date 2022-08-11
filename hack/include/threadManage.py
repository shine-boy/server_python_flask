
#  coding=utf-8
import time
from datetime import datetime
import threading


class ThreadManage:

    def __init__(self,maxthreading=1000):
        # 不可太小，其他程序也会占用线程数
        self.threadingNum=maxthreading
        self.threads=[]
        self.active = False
        self.running = []
    def __del__(self):
        for i in self.threads:
            pass;
        self.threads.clear()

    def waiter(self):
        try:
            while len(self.running) > 0:
                temp = self.running.pop()
                if temp.is_alive():
                    self.running.append(temp)
                    time.sleep(1)

        except Exception as e:
            print('end'+ e)

    def add(self,fun, args=(),*, timeout=120, endtime=None):
        temp = threading.Thread(target=fun, args=args)
        result = self.threads
        now = datetime.now()
        self.threads = [{
            'endTime': endtime or datetime.fromtimestamp(now.timestamp() + timeout),
            'thread': temp
        }]
        self.threads.extend(result)

    def run(self):
        if self.active is True:
            return
        def do():
            while True:
                try:
                    obj = self.threads.pop()
                    temp = obj.get('thread')
                    now = datetime.now()
                    if obj.get('endTime') < now:
                        continue
                    activeCount = threading.activeCount()
                    if activeCount <= self.threadingNum:
                        temp.start()
                        self.running.append(temp)
                    else:
                        self.threads.append(obj)
                        time.sleep(1)
                        # print("可活动线程数：%d" % self.threadingNum)
                        # print("活动线程数：%d" % activeCount)
                except Exception as e:
                    print('threadManage',e)
                    time.sleep(1)
                    break

        temp = threading.Thread(target=do)
        temp.run()
        self.active = False


threadManage=ThreadManage(1000)

if __name__ == '__main__':
    stock=ThreadManage(1)
    def te(i):
        time.sleep(10)
        print('hh', i)
    now = datetime.now()
    print(datetime.fromtimestamp(now.timestamp() + 20), now)
    for i in range(4):
        print(i)
        stock.add(te, (i,),timeout=10)
    stock.run()
    stock.waiter()
    print('start')
    # stock.waiter()

