
#  coding=utf-8
import time
from datetime import datetime
import threading

threadLock = threading.Lock()
class ThreadManage:

    def __init__(self,maxthreading=1000):
        # 不可太小，其他程序也会占用线程数
        self.threadingNum=maxthreading
        self.threads=[]
        self.active = False

    def __del__(self):
        for i in self.threads:
            pass;
        self.threads.clear()

    def waiter(self):
        while len(self.threads) >0:
            time.sleep(1)

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
                    else:
                        self.threads.append(temp)
                        time.sleep(1)
                        print("可活动线程数：%d" % self.threadingNum)
                        print("活动线程数：%d" % activeCount)
                except Exception as e:
                    print(e)
                    time.sleep(1)
                    break

        temp = threading.Thread(target=do)
        temp.run()
        self.active = True






if __name__ == '__main__':
    stock=ThreadManage(1)
    def te(i):
        time.sleep(10)
        print('hh', i)
    now = datetime.now()
    print(datetime.fromtimestamp(now.timestamp() + 20), now)
    for i in range(1):
        print(i)
        stock.add(te, (i,),timeout=10)
    stock.run()
    print('start')
    # stock.waiter()

