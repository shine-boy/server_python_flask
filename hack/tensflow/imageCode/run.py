
#coding=utf-8
import tensorflow as tf
import math
import os
from matplotlib import pyplot as plt
import numpy as np
import  tensorflow.keras.preprocessing.image as Img
import cv2
modelpath = 'save_model/my_model'
def createModel():

    model = tf.keras.models.Sequential([
        tf.keras.layers.Flatten(input_shape=(28, 28)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(10, activation='softmax')

    ])
    return model

def trainModel():
    mnist = tf.keras.datasets.mnist
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train, x_test = x_train / 255.0, x_test / 250.0

    model = createModel()

    model.compile(optimizer='adam',
                  loss='sparse_categorical_crossentropy',
                  metrics=['accuracy'])

    checkpoint_path = 'training/imageCode.ckpt'
    checkpoint_dir = os.path.dirname(checkpoint_path)
    cp_callpack = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                     save_weights_only=True,
                                                     verbose=1)
    # model.load_weights(checkpoint_path)
    model.fit(x_train, y_train, epochs=5,
              callbacks=[cp_callpack])

    model.save(modelpath)
    test_loss, test_acc = model.evaluate(x_test, y_test, verbose=2, )
    print('loss:%f, acc:%f'%(test_loss, test_acc))

def predictMoel(img):
    model = tf.keras.models.load_model(modelpath)
    result = model.predict(img)
    print(result)
    for re in result:
        print(np.argmax(re))

# 内容描粗
def resize(img, dsize):
    print(dsize)
    ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    if dsize[0] > 0:
        kernel = np.ones(dsize, np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
    else:
        kernel = np.ones((-dsize[0],-dsize[1]), np.uint8)
        img = cv2.erode(img, kernel, iterations=1)
    # 阙值化
    # ret, temp = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)

    # temp = cv2.dilate(temp, kernel, iterations=1)

    ret, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)
    return img
    pass


# 获取图像内容的粗细
def thickness(img):
    lis = []
    for x in img:
        max = 0
        l = 0
        for y in x:
            if y < 127:
                l += 1
            else:
                if max < l:
                    max = l
                l = 0
        if max < l:
            max = l
        if max > 0:
            lis.append(max)
    print(lis)
    return np.average(lis)

# 把一个图片分割成多个 如： 含1、2、3、4的图片拆分开
def split(img):
    lis=[]
    while True:
        temp, xl, yl = area(img)
        if len(temp) == 0:
            break
        lis.append(temp)
        img = img[:,yl:]
    return lis

# 标准化，把图片内容粗细趋于标准
# 标准图为28像素，内容有4像素值粗细
def norm(img):
    thick = thickness(img)
    wei, hig = img.shape
    print(wei/(28/3.64),thick,wei)
    l = round((wei/(28/3.64)) - thick)
    img =resize(img,(l, l))
    return img


# 获取图形内容区域，消除多余空白部分
def area(img):
    xl, yl = [0, 0], [0, 0]
    wei, hei = img.shape
    # lx, ly = round(wei/10), round(hei/10)
    lx, ly = 1, 1
    temp = np.transpose(img)
    for i in range(hei):
        l_ = i + ly
        if l_ > hei:
            l_ = hei
        if np.min(temp[i:l_]) < 127:
            if yl[0] == 0:
                yl[0] = i
            else:
                yl[1] = l_
        elif yl[1] > 0:
            break

    if yl[0] != 0:
        for i in range(wei):
            l_ = i + lx
            if l_ > wei:
                l_ = wei
            if np.min(img[i:l_,yl[0]:yl[1]]) < 127:
                if xl[0] == 0:
                    xl[0] = i
                else:
                    xl[1] = l_
            elif xl[1] > 0:
                break
    return img[xl[0]:xl[1], yl[0]:yl[1]], xl[1], yl[1]


def show(imgs):
    l = len(imgs)
    if l > 1:
        r = math.ceil(math.sqrt(l))
        c = math.ceil(math.sqrt(l))
        i = 0
        for img in imgs:
            plt.subplot(r, c, i+1)
            plt.imshow(img)
            i += 1
    else:
        plt.imshow(imgs[0])
    plt.show()

# 填充为正方形
def fill(img):
    wei, hei = img.shape
    def fill_(img_, fi, w, h):
        temp = np.zeros((fi, h))
        temp.fill(255)
        img_ = np.insert(img_, w, temp, axis=0)
        img_ = np.insert(img_, 0, temp, axis=0)
        return img_
    # print(thick)
    fi = math.ceil(min(round(min(wei, hei)/(28/3.64)*5), 100)/2)
    f = fi

    if wei > hei:
        f = round((wei - hei) / 2) + fi

    img = np.transpose(img)
    img = fill_(img, f, hei, wei)
    img = np.transpose(img)
    if wei < hei :
        hei += f * 2
        f = round((hei - wei) / 2) + fi
    else:
        hei += f * 2
        f = fi
    img = fill_(img, f, wei, hei)
    return img


if __name__ == '__main__':
    # img = cv2.imread(path, 0)
    img = cv2.imread('C:\\Users\wu\Desktop\\code1.bmp', 0)
    # img = img / 255.0
    # split()

    # predictMoel(np.array([img]))
    mnist = tf.keras.datasets.mnist
    (x_train, y_train), (x_test, y_test) = mnist.load_data()

    lis = []
    # lis.append(img)
    # img1 = x_test[3]
    # lis.append(img1)
    # ret, img = cv2.threshold(img, 127, 255, 0)
    # contours, hierarchy = cv2.findContours(img,1,2)
    # print(contours)
    # cnt= contours[0]
    # for  cnt in contours:
    #     x, y ,w ,h =cv2.boundingRect(cnt)
    #     img2=cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0), 2)
    #     lis.append(img2)

    temp = cv2.imread('C:\\Users\wu\Desktop\\IMG_20210523_185136.jpg')
    rows, cols ,ch =temp.shape

    pts1 = np.float32([[2611, 768],[37.450, 2019],[209, 1230],  [610, 2982] ])
    pts2 = np.float32([[0, 0], [2000, 0], [0, 2000], [2000, 2000]])
    lis.append(temp)
    M = cv2.getPerspectiveTransform(pts1, pts2)
    dst = cv2.warpPerspective(temp, M, (2000, 2000))
    lis.append(dst)
    # ret, img1 = cv2.threshold(img1, 127, 255, cv2.THRESH_BINARY_INV)
    # img1 = split(img1)[0]
    # lis=split(img)
    # lis.append(img)
    # lis.append(img1)
    # for i in range(len(lis)):
    #     lis[i] = fill(lis[i])
    #     lis[i] = norm(lis[i])
    #     lis[i] = cv2.resize(lis[i], (28,28))
    #     ret, lis[i] = cv2.threshold(lis[i], 127, 255, cv2.THRESH_BINARY_INV)
    #
    # print(type(lis))
    # predictMoel(np.array(lis))

    show(lis)