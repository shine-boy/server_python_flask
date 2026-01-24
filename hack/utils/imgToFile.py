import math

from pydub import AudioSegment
import numpy as np
import cv2
import struct
def toImage():
    f = open('D:\\git\\Util - 副本.rar', 'rb')

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

    for i in range( weight-len(arr[len(arr) - 1])):
        arr[len(arr) - 1].append(0)

    print(np.array(arr).flatten().size, np.array(arr).flatten())
    f = open(r'D:\\git\\testTxt', 'w')
    savetext = ''.join(hex(i)[2:] for i in np.array(arr).flatten())

    savetext = savetext[:-weight-len(arr[len(arr) - 1])]
    f.write(savetext)
    print(
        "max",
        weight,
        len(arr),
        len(arr[len(arr) - 1]),
        len(arr[len(arr) - 2])
    )
    name = str(ll)
    cv2.imwrite('D:\\git\\' + name + '.png', np.array(arr))
    f.close()


def imageToFile():
    f = cv2.imread('C:\\Users\\w30038925\\Downloads\\27129058.png', 0)
    arr = []
    for i in range(len(f)):
        arr.append([])
        for j in range(len(f[0])):
            arr[i].append(f[i][j])

    arr = np.array(arr).flatten()
    l = len(arr)
    arr = np.delete(arr, range(l - 22,l), 0)

    data = bytes(arr)

    print(len(data), l, len(arr))

    f = open(r'D:\\git\\Util - test.rar', 'wb')
    f.write(data)
    f.close()

# eg: m4a转MP3   trans_m4a_to_other('input/录音.m4a', 'MP3')
def trans_m4a_to_other(filepath, hz):
    song = AudioSegment.from_file(filepath)
    song.export('newSong.'+str(hz), format=str(hz))

import wave


class AudioHandel:

    def getAudioContent(self, data):
        starts = []
        ends = []
        l = len(data)
        for i in range(100,l):

            if data[i] > 0:
                break
            starts.append(data[i])
        for i in sorted(range(l), reverse=True):
            if data[i] > 0:
                break
            ends.append(data[i])
        print(len(data),len(starts), -len(ends))
        result = data[len(starts)+100: -len(ends)]
        return result

    def getAudioContentByPath(self,path):
        wr = wave.open(path, 'rb')
        # 返回声道数量（1为单声道， 2为立体声）
        channels = wr.getnchannels()
        #  返回采样字节长度
        sampwidth = wr.getsampwidth()
        # 返回采样频率
        # print(wr.getframerate())
        # 返回音频总的帧数
        frames = wr.getnframes()
        l = frames * channels * sampwidth
        data = wr.readframes(l)
        wr.close()
        return  data


    def p3test(self):

        result1 = self.getAudioContentByPath('D:\\360安全浏览器下载\\1.wav')
        result2 = self.getAudioContentByPath('D:\\360安全浏览器下载\\2.wav')
        result = result1 + result2

        print(len(result), result)
        ww = wave.open('D:\\360安全浏览器下载\\tes.wav', 'wb')
        ww.setnchannels(1)
        ww.setsampwidth(2)
        ww.setframerate(22050)
        ww.writeframes(bytes(result))
        ww.close()

    def toAudio(self):
        f = open('D:\\git\\testTxt', 'r')

        data = f.read()
        l = len(data)
        print(l)
        result = []
        start = 0
        for i in data:
            start+=1
            print(i, start, (start/l)*100,'%')
            result += self.getAudioContentByPath('D:\\git\\study\\GPT-SoVITS-main\\input\\' + str(i).upper() + '.wav')

        ww = wave.open('D:\\360安全浏览器下载\\tes.wav', 'wb')
        ww.setnchannels(1)
        ww.setsampwidth(2)
        ww.setframerate(22050)
        ww.writeframes(bytes(result))
        ww.close()

    def create(self):
        from ttskit import sdk_api
        keys = '0,1,2,3,4,5,6,7,8,9,A,B,C,D,E,F'.split(',')
        map = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            'A': '欸',
            'B': '币',
            'C': '谁',
            'D': '地',
            'E': '益',
            'F': '符',


        }
        # keys = ['0']
        keyMap = {}
        for key in keys:
            result = self.getAudioContent(sdk_api.tts_sdk(map[key], audio='24'))
            keyMap[key] = result
            ww = wave.open('D:\\git\\study\\GPT-SoVITS-main\\input\\' + key + '.wav', 'wb')
            ww.setnchannels(1)
            ww.setsampwidth(2)
            ww.setframerate(22050)
            ww.writeframes(bytes(result))
            ww.close()

def auodio():
    from ttskit import http_server

    http_server.start_sever()
    # 打开网页：http://localhost:9000/ttskit

def audioToText():
    import whisper

    model = whisper.load_model("base")
    result = model.transcribe('D:\\360安全浏览器下载\\1.wav')
    print(result["text"])

if __name__ == '__main__':
    # plt.imsave()
    # toImage()
    pass
    # audioHandel = AudioHandel()
    # audioHandel.toAudio()
    # audioToText()

    # print(keyMap)
    imageToFile()
    # print(torch.cuda.device_count())
    # p3test()
    # auodio()
    # trans_m4a_to_other('input/录音.m4a', 'wav')