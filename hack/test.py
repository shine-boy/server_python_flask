# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

import time
from os import fdopen


def study():
    tasks = {
        'execute_daily_job': {
            'name': 'execute_daily_job',
            'description': '当前时间作业'
        },
        "selection_data_daily_job": {
            'name': 'selection_data_daily_job',
            'description': '综合选股作业'
        },
        "backtest_data_daily_job": {
            'name': 'backtest_data_daily_job',
            'description': '基础数据收盘2小时后作业'
        },
        "basic_data_other_daily_job": {
            'name': 'basic_data_other_daily_job',
            'description': '基础数据非实时作业'
        },
        'indicators_data_daily_job': {
            'name': 'indicators_data_daily_job',
            'description': '指标数据作业'
        },
        'klinepattern_data_daily_job': {
            'name': 'klinepattern_data_daily_job',
            'description': 'K线形态作业'
        },
        'strategy_data_daily_job': {
            'name': 'strategy_data_daily_job',
            'description': '策略数据作业'
        },
        'backtest_data_daily_job': {
            'name': 'backtest_data_daily_job',
            'description': '回测数据'
        },

    }
    print(list(map(lambda x: tasks.get(x), tasks)))
    for i in range(4):
        print(i)
        ''.split()


import requests
url = 'http://localhost:3001/'

def getFetch(params):
    headers = {'Content-Type': 'application/json'}  # 设置请求头
    response = requests.post(url+'drawServer/updateOne', json=params, headers=headers)
    if response.status_code == 200:
        data = response.json()  # 假设返回的是JSON格式的数据
        return data
    else:
        print('Failed to retrieve data')
    return  None

if __name__ == '__main__':
    # study()
    print(datetime.fromtimestamp(1764918001000/1000))
    strf = datetime.fromisoformat('2025-12-05 15:00:01')
    print(datetime.now())
    print(strf)
    now = datetime.now()
    print(now.strftime("%H:%M:%S"))
    # ttt = datetime(now.year, now.month,now.day,17)
    ttt = datetime(2020, 12, 30, 17)
    print(strf< ttt)
    timestamp = 1609459200  # 假设时间戳为2021-01-01 00:00:00

    # 方法一：使用time模块的strftime函数将时间戳格式化为指定的时间字符串
    time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
    print(time_str.replace('-', ''))
    print('444' in ['300'])
    while True:
        now = datetime.now()
        print(now.strftime('%H:%M:%S'))
        time.sleep(1)