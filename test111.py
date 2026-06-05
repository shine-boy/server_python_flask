import math
import sys
import numpy as np
import cv2
def toImage(filename=None):
    name = 'D:\\git\\Util - 副本.rar'
    if filename is not None:
        name = fileName
    f = open(name, 'rb')

    arr = []

    data = f.read()
    l = len(data)

    weight = math.ceil(math.sqrt(l))

    max = 0;
    print(l)
    for i in range(l) :
        if i %weight == 0:
            # print(math.floor(i / weight), data[i])
            arr.append([data[i]])
            # arr[math.floor(i / weight)] =
        else:
            arr[math.floor(i / weight)].append(data[i])

    print(arr[len(arr) - 1], len(arr[len(arr) - 1]))
    ll = weight-len(arr[len(arr) - 1])

    for i in range( ll):
        arr[len(arr) - 1].append(0)

    # 构造成正方形， 看需要是否加上
    prelen = len(arr)
    for i in range(weight- len(arr)):
        arr.append([])
        for j in range(weight):
            arr[prelen + i].append(0)

    print(np.array(arr).flatten().size, np.array(arr).flatten())
    f = open(r'D:\\git\\testTxt', 'w')
    savetext = ''.join(hex(i)[2:] for i in np.array(arr).flatten())

    savetext = savetext[:-ll]
    f.write(savetext)
    print(
        "max",
        weight,
        len(arr),
        len(arr[len(arr) - 1]),
        len(arr[len(arr) - 2])
    )
    name = str(ll)
    pathname = 'D:\\git\\' + name + '.png'
    print('pathname', pathname)
    cv2.imwrite(pathname, np.array(arr))
    f.close()


def imageToFile(filename=None, add=0):
    name = 'D:\\git\\93.png'
    if filename is not None:
        name = fileName
    f = cv2.imread(name, 0)
    arr = []
    for i in range(len(f)):
        arr.append([])
        for j in range(len(f[0])):
            arr[i].append(f[i][j])

    arr = np.array(arr).flatten()
    l = len(arr)
    arr = np.delete(arr, range(l - add,l), 0)

    data = bytes(arr)

    f = open(r'E:\\git\\imageToFile.zip', 'wb')
    f.write(data)
    f.close()
    print(data)





if __name__ == '__main__':
    # plt.imsave()
    # toImage()
    pass
    # audioHandel = AudioHandel()
    # audioHandel.toAudio()
    # audioToText()
    fileName = None
    if len(sys.argv) > 1:
        fileName = sys.argv[1]
    if fileName and fileName.endswith('.zip'):
        toImage(fileName)
        pass
    else:
        imageToFile(fileName, int(sys.argv[2]))
    # print(keyMap)
    # print(torch.cuda.device_count())
    # p3test()
    # auodio()
    # trans_m4a_to_other('input/录音.m4a', 'wav')
