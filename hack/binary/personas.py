#coding=utf-8
#赛事概要   ·https://challenge.xfyun.cn/topic/info?type=user-portrait&ch=dc-web-20
# 一、赛事背景
# 讯飞AI营销云基于深耕多年的人工智能和大数据技术，赋予营销智慧创新的大脑，以健全的产品矩阵和全方位的服务，帮助广告主用AI+大数据实现营销效能的全面提升，打造数字营销新生态。
#
# 二、赛事任务
# 基于用户画像的产品推荐，是目前AI营销云服务广告主的一项重要能力，本次赛题选择了两款产品分别在初赛和复赛中进行用户付费行为预测，参赛选手需基于提供的样本构建模型，预测用户是否会购买相应商品。


import os
import pandas as pd
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from datetime import datetime
def getData_():
    names = ['pid', 'label', 'gender', 'age', 'tagid', 'time', 'province', 'city', 'model', 'make']
    df = pd.read_table('./data/train.txt', sep=',', header=None, names=names)
    print(df.head().to_json(orient='records'))

    result = []
    print('总数:%d' % df.shape[0])
    for name in names:
        print('存在%s:%d' % (name, df[pd.isnull(df[name]) == False].shape[0]))
    #     把年龄为nan的设置为0
    df['age'][pd.isnull(df['age'])] = 0
    #   把性别为NAN的设置为 2
    df['gender'][pd.isnull(df['gender'])] = 2

    train_x = df[['gender', 'age', 'tagid']].to_json(orient='records')
    train_x = json.loads(train_x)

    max = 0
    for i in range(len(train_x)):
        ids = json.loads(train_x[i]['tagid'])
        del train_x[i]['tagid']
        for id in ids:
            train_x[i][id] =id
        if len(ids) > max:
            max = len(ids)
    print('max:%d'%max)
    result = np.array(result)
    print(pd.DataFrame(train_x))

    train_y = np.array(df['label'])
    return result, np.array(train_y), max
    # print(type(json.loads(tagids[0])))

# 把数组字符转换为某数组，取每个数显的字符，然后分类
def tonumber(pre):
    lis = []
    for i in pre:
        try:
            lis.index(i)
        except Exception as e:
            lis.append(i)
    max = len(pre)
    for i in range(max):
        pre[i] = lis.index(pre[i])/float(max)
    return pre

def getData(path = './data/train.txt'):
    names = ['pid', 'label', 'gender', 'age', 'tagid', 'time', 'province', 'city', 'model', 'make']
    df = pd.read_table(path, sep=',', header=None, names=names)
    print(df.head().to_json(orient='records'))

    result = []
    print('总数:%d' % df.shape[0])
    for name in names:
        print('存在%s:%d' % (name, df[pd.isnull(df[name]) == False].shape[0]))
    #     把年龄为nan的设置为0
    df['age'][pd.isnull(df['age'])] = 0
    #   把性别为NAN的设置为 2
    df['gender'][pd.isnull(df['gender'])] = 2
    train_y = df['label']
    train_x = df[[ 'gender','label', 'age', 'province', 'city', 'model', 'make']]
    train_x['province'] = tonumber(list(train_x['province']))
    train_x['city'] = tonumber(list(train_x['city']))
    train_x['model'] = tonumber(list(train_x['model']))
    train_x['make'] = tonumber(list(train_x['make']))
    result = np.array(train_x)

    return train_x
    # print(type(json.loads(tagids[0])))
def getData_test(path = './data/train.txt'):
    names = ['pid', 'gender', 'age', 'tagid', 'time', 'province', 'city', 'model', 'make']
    df = pd.read_table(path, sep=',', header=None, names=names)
    print(df.head().to_json(orient='records'))

    result = []
    print('总数:%d' % df.shape[0])
    for name in names:
        print('存在%s:%d' % (name, df[pd.isnull(df[name]) == False].shape[0]))
    #     把年龄为nan的设置为0
    df['age'][pd.isnull(df['age'])] = 0
    #   把性别为NAN的设置为 2
    df['gender'][pd.isnull(df['gender'])] = 2
    train_x = df[['pid', 'gender', 'age', 'province', 'city', 'model', 'make']]
    train_x['province'] = tonumber(list(train_x['province']))
    train_x['city'] = tonumber(list(train_x['city']))
    train_x['model'] = tonumber(list(train_x['model']))
    train_x['make'] = tonumber(list(train_x['make']))
    result = np.array(train_x)

    return train_x
def build_model(shape):
    # # 输入形状是用于电影评论的词汇数目（10,000 词）
    # vocab_size = 10000
    # model = keras.Sequential()
    # model.add(keras.layers.Embedding(vocab_size, 16))
    # model.add(keras.layers.GlobalAveragePooling1D())
    # model.add(keras.layers.Dense(16, activation='relu'))
    # model.add(keras.layers.Dense(1, activation='sigmoid'))
    model = keras.Sequential([
        layers.Dense(128, activation='relu', input_shape=[shape]),
        layers.Dense(64, activation='relu'),
        layers.Dense(1, activation='sigmoid')
      ])

    optimizer = tf.keras.optimizers.RMSprop(0.00001)

    model.compile(loss='mse',
                optimizer=optimizer,
                metrics=['mae', 'mse', 'accuracy'])
    return model

def norm(data):
    train_stats = data.describe()

    print(train_stats)
    print(train_stats.loc['mean'])
    return (data - train_stats.loc['mean']) / train_stats.loc['std']

def predict():
    x = getData()
    # x_test, y_test = getData('./data/apply_new.txt')
    train_dataset = x.sample(frac=0.8, random_state=0)
    test_dataset = x.drop(train_dataset.index)

    train_labels = train_dataset.pop('label')
    test_labels = test_dataset.pop('label')
    new_model = tf.keras.models.load_model('saved_model/my_model')
    loss, mae, mse = new_model.evaluate(test_dataset,  test_labels, verbose=2)
    print(loss)
    print(mae)
    print(mse)
    # print('Restored model, accuracy: {:5.2f}%'.format(100*acc))

def create():
    x = getData()
    # x_test, y_test = getData('./data/apply_new.txt')
    train_dataset = x.sample(frac=0.8, random_state=0)
    test_dataset = x.drop(train_dataset.index)

    train_labels = train_dataset.pop('label')
    test_labels = test_dataset.pop('label')
    print(test_dataset)
    print(test_labels)
    # print(train_data)
    model = build_model(len(train_dataset.keys()))
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
        train_dataset, train_labels,
        epochs=1000,
        validation_split=0.2, verbose=1,
        validation_data=(test_dataset, test_labels),
        callbacks=[cp_callback, early_stop, tensorboard_callback])

    loss, mae, mse, accuracy = model.evaluate(test_dataset, test_labels, verbose=2)
    print(loss)
    print(mae)
    print(mse)
    print(accuracy)
    model.save('saved_model/my_model')
    # test_predictions = model.predict(x).flatten()
    # print(y[:10])
    # print(test_predictions[:10])

# 得到提交结果
def predict_data():
    x=getData_test('./data/apply_new.txt')
    pid = x.pop('pid')
    new_model = tf.keras.models.load_model('saved_model/my_model')
    test_predictions = new_model.predict(x).flatten()
    test_predictions[test_predictions<0.5] = 0
    test_predictions[test_predictions >= 0.5] = 1
    date = pd.DataFrame()
    date['user_id'] = pid
    date['category_id'] = test_predictions
    date.to_csv('./data/submit.csv',index=False)
    print(date)

    # print(y[:10])
    # print(test_predictions[:10])

if __name__ == '__main__':
    # # predict()
    create()
    # predict_data()
    #