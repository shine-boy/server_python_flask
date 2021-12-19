

from hack.spider.jipiao import Jipiao
from datetime import datetime,date
from hack.include.myIterator import MyIterator
import calendar
import math

import requests
def getMinJiPiao():
    jip=Jipiao()
    start=['上海','杭州','无锡','徐州','南京','常州']
    end="昆明"
    space=['2021-02-08','2021-02-11']
    times=[]
    result=[]
    for s in start:
        data=jip.qunaLvXing(start=s,end=end,now='2021-02')
        if data is not None:
            result.append(data.get('price'))
    print(result)


def test():
    for i in ["temp1"]:
        yield i
if __name__ == '__main__':
    # getMinJiPiao()
    jip = Jipiao()
    print(jip.getMin())
    pass