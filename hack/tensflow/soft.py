
# import pathlib
#

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from hack.util import mongodb_connect
import sys
import pymongo
import io
# import seaborn as sns
#
from datetime import datetime
import tensorflow as tf
# #
from tensorflow import keras
from tensorflow.keras import layers


myclient = pymongo.MongoClient("mongodb://192.168.142.1:27017")
mydb = myclient['dongfangcaifu']
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='gb18030')


def find(lis, target):
    try:
        lis.index(target)
        return True
    except ValueError as v:
        return False


def findIndex(lis, target):
    index = -1
    try:
        index = lis.index(target)
    except ValueError as v:
        return index
    return index


# 划分各类别数据，并得到分类列表
def divide_type(label, types=[]):
    alldata = []
    data = []
    if os.path.exists('./types.txt') is False:
        with open('./types.txt', 'w') as f:
            f.close()
    with open('./types.txt', 'r') as f:
        alldata = f.readlines()
        f.close()
    with open('./types.txt', 'w') as f:
        labels = []
        if len(alldata) > 0:
            labels = alldata[0][:-1].split("\t")
        else:
            alldata.append(labels)
        index = findIndex(labels, label) + 1
        print(index)

        if index > 0:
            data = alldata[index][:-1].split("\t")
        else:
            labels.append(label)
        alldata[0] = '\t'.join(labels) + '\n'
        for type in types:
            if find(data, type) is False:
                data.append(type)
        if index > 0:
            alldata[index] = '\t'.join(data) + '\n'
        else:
            alldata.append('\t'.join(data) + '\n')

        f.writelines(alldata)
        # numpy.fromfile('./types',sep=' ')
        f.close()
    return data


# 归一
def to_one(label, dataFrame):
    column = dataFrame[label].copy()
    types = divide_type(label, column.unique())
    print(types)
    for i in range(column.size):
        column.loc[i] = findIndex(types, column[i])
    dataFrame[label] = column
    return column

def getStockData():
    names=mydb['names'].find({})
    # names=list(ns)
    result=[]
    def isNext(current,next):
        t=next.timestamp()-current.timestamp()
        if t>110 and t<130:
            return True
        return False

    for name in names:
        code=name['code']
        item=mydb[code].find({},{'_id':0}).sort([('time',1)])
        current=item.next()
        for next in item:
            if isNext(current['time'],next['time']):
                current['next2']=next['f43']
                result.append(current)
            current=next
    data=pd.DataFrame(result)
    data.to_csv("../data/stock.csv",index=False)
    # print(data.head())

        # print(list(item))

def getData():
    column_names =  ["city", 'openTime', 'region', 'province', 'address', 'decoration', 'houseType', 'volumeRatio',
            'greenRate', 'proYears', 'planHouse', 'parkRatio', 'towards', 'proComp', 'developer', 'apartment',
            'buildType','source','secondOrNew','buildArea','avgPrice']

    raw_dataset = pd.read_csv('../data/house.csv', names=column_names,low_memory=False,
                              na_values="?", comment='\t',
                               skipinitialspace=True)
    dataset = raw_dataset.copy()

    print(dataset.isna().sum())

def build_model(shape):
  model = keras.Sequential([
    layers.Dense(128, activation='relu', input_shape=[shape]),
    layers.Dense(64, activation='relu'),
    layers.Dense(1)
  ])

  optimizer = tf.keras.optimizers.RMSprop(0.00001)

  model.compile(loss='mse',
                optimizer=optimizer,
                metrics=['mae', 'mse'])
  return model

class PrintDot(keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs):
        if epoch % 100 == 0:
            print('')
        print('.', end='')

def plot_history(history):
    hist = pd.DataFrame(history.history)
    hist['epoch'] = history.epoch
    print(hist.tail())
    plt.figure()
    plt.xlabel('Epoch')
    plt.ylabel('Mean Abs Error [MPG]')
    plt.plot(hist['epoch'], hist['mae'],
             label='Train Error')
    plt.plot(hist['epoch'], hist['val_mae'],
             label='Val Error')
    plt.ylim([0, 5])
    plt.legend()

    plt.figure()
    plt.xlabel('Epoch')
    plt.ylabel('Mean Square Error [$MPG^2$]')
    plt.plot(hist['epoch'], hist['mse'],
             label='Train Error')
    plt.plot(hist['epoch'], hist['val_mse'],
             label='Val Error')
    plt.ylim([0, 20])
    plt.legend()
    plt.show()

class Stock_data:
    def __init__(self, code, startDate=None):
        myMongo = mongodb_connect()
        self.mydb = myMongo['dongfangcaifu'][code]
        self.startDate = startDate
        self.data = []
        self.get_data()

    def get_data(self):
        keys = ['time', 'f11', 'f12', 'f13', 'f15', 'f17', 'f19', 'f31', 'f33', 'f35', 'f37', 'f39', 'f43', 'f44', 'f45',
               'f46', 'f47', 'f48', 'f49', 'f50','f52', 'f60', 'f71', 'f135', 'f136', 'f137', 'f138', 'f139', 'f141', 'f142', 'f144', 'f145',
               'f147', 'f148', 'f161', 'f168', 'f169', 'f170']
        query = {}
        if self.startDate:
            query['time'] = {"$gte": self.startDate}
        sort = [("time", -1)]
        projection = {
            '_id': 0
        }
        for key in keys:
            projection[key] = 1
        result = self.mydb.find(query, projection).sort(sort)
        result = list(result)
        startYear = datetime(year=2020, month=1, day=1)
        def should_remove(item):
            for i in item:
                print(type(item[i]))
                if type(item[i]) is not int and type(item[i]) is not float:
                    return True
            return False
        for res in result:
            res['time'] = (res['time'].timestamp() - startYear.timestamp()) * 1000
            # 当天交易时间9：30 = 0， 15：00 = 5.5*60*60, 减8是因为时间格式
            res['c_time'] = res['time'] % (24 * 60 * 60 * 1000) - (9.5 - 8) * 60 * 60 * 1000
            if should_remove(res) is False:
                self.data.append(res)

# 以前的main方法
def pre_main():
    raw_dataset = pd.read_csv('../data/stock.csv', low_memory=False,
                              na_values="?", comment='\t', index_col=[0],
                              skipinitialspace=True)
    dataset = raw_dataset.copy()
    dataset.pop('time')
    print(dataset.size)
    # dataset.replace(str('-'),np.nan)
    # dataset.dropna()
    dataset = dataset[~dataset.isin([str('-'), '-', np.NaN])]
    dataset = dataset.dropna()
    print(dataset.size)
    # dataset.pop("f58")
    # to_one('f127', dataset)
    # to_one('f128', dataset)
    # code=dataset['f57']
    # code=map(lambda x:int(x),code)
    # dataset['f57']=list(code)
    # dataset.to_csv("../data/stock.csv")
    train_dataset = dataset.sample(frac=0.8, random_state=0)
    test_dataset = dataset.drop(train_dataset.index)

    train_labels = train_dataset.pop('next2')
    test_labels = test_dataset.pop('next2')

    train_dataset = train_dataset.astype('float64', errors='ignore')
    test_dataset = test_dataset.astype('float64', errors='ignore')
    train_stats = train_dataset.describe()
    # 转置
    train_stats = train_stats.transpose()
    print(train_stats)
    print(train_dataset.keys())

    # 数据规范化，归一化
    def norm(x):
        return (x - train_stats['mean']) / train_stats['std']

    normed_train_data = norm(train_dataset)
    normed_test_data = norm(test_dataset)

    model = build_model(len(train_dataset.keys()))
    model.summary()

    early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)

    checkpoint_path = "training/cp.ckpt"
    checkpoint_dir = os.path.dirname(checkpoint_path)
    print('file')
    print(checkpoint_dir)
    # 创建一个保存模型权重的回调
    cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                     save_weights_only=True,
                                                     verbose=1)
    train_labels = train_labels.astype('float64', errors='ignore')
    test_labels = test_labels.astype('float64', errors='ignore')

    log_dir = "logs/fit/" + datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    history = model.fit(
        normed_train_data, train_labels,
        epochs=1000,
        validation_split=0.2, verbose=0,
        validation_data=(test_dataset, test_labels),
        callbacks=[cp_callback, early_stop, tensorboard_callback])

    loss, mae, mse = model.evaluate(normed_test_data, test_labels, verbose=2)
    print(loss)
    print(mae)
    print(mse)
    model.save('saved_model/my_model')
    # plot_history(history)
    test_predictions = model.predict(normed_test_data).flatten()
    print(test_labels[:10])
    print(test_predictions[:10])

    pass

def test_spft():
    stockdata = Stock_data('000002')
    print(stockdata.data)
    raw_dataset = pd.DataFrame(stockdata.data)
    dataset = raw_dataset.copy()
    train_dataset = dataset.sample(frac=0.8, random_state=0)
    test_dataset = dataset.drop(train_dataset.index)

    # 被目标值的定义卡住，目标值应该是之后哪个时间的成交价， 如果‘之后’这个时间固定的话又固定为什么
    train_labels = train_dataset.pop('next2')
    test_labels = test_dataset.pop('next2')

    train_dataset = train_dataset.astype('float64', errors='ignore')
    test_dataset = test_dataset.astype('float64', errors='ignore')
    train_stats = train_dataset.describe()
    # 转置
    train_stats = train_stats.transpose()
    print(train_stats)
    print(train_dataset.keys())

    # 数据规范化，归一化
    def norm(x):
        return (x - train_stats['mean']) / train_stats['std']

    normed_train_data = norm(train_dataset)
    normed_test_data = norm(test_dataset)

    model = build_model(len(train_dataset.keys()))
    model.summary()

    early_stop = keras.callbacks.EarlyStopping(monitor='val_loss', patience=10)

    checkpoint_path = "training/cp.ckpt"
    checkpoint_dir = os.path.dirname(checkpoint_path)
    print('file')
    print(checkpoint_dir)
    # 创建一个保存模型权重的回调
    cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                     save_weights_only=True,
                                                     verbose=1)
    train_labels = train_labels.astype('float64', errors='ignore')
    test_labels = test_labels.astype('float64', errors='ignore')

    log_dir = "logs/fit/" + datetime.now().strftime("%Y%m%d-%H%M%S")
    tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir, histogram_freq=1)

    history = model.fit(
        normed_train_data, train_labels,
        epochs=1000,
        validation_split=0.2, verbose=0,
        validation_data=(test_dataset, test_labels),
        callbacks=[cp_callback, early_stop, tensorboard_callback])

    loss, mae, mse = model.evaluate(normed_test_data, test_labels, verbose=2)
    print(loss)
    print(mae)
    print(mse)
    model.save('saved_model/my_model')
    # plot_history(history)
    test_predictions = model.predict(normed_test_data).flatten()
    print(test_labels[:10])
    print(test_predictions[:10])

    pass
if __name__ == '__main__':
    stockdata= Stock_data('000002')
    print(stockdata.data)
    df = pd.DataFrame(stockdata.data)
    print(df)
