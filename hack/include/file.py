# coding=utf-8
import os
import shutil


class File:
    def __init__(self,path):
        self.path=path


    # 文件拆封，把大文件拆分为小文件
    def split(self,todir,chunkSize=1020*1024*200):
        if not os.path.exists(todir):
            os.mkdir(todir)
        partNum=0
        with open(self.path,'rb') as inputFile:
            while True:
                chunk=inputFile.read(chunkSize)
                if not chunk:
                    break
                partNum+=1
                fileName=os.path.join(todir,("part%04d"%partNum))

                with open(fileName,'wb') as partFile:
                    partFile.write(chunk)
                    partFile.close()
                pass
            inputFile.close()

    # 合并文件
    def merge(self):
        pass

if __name__ == '__main__':

    # fi=File("F:\movies.zip")
    # fi.split("F:\part",1024*1024*1800)
    path = 'Redmi K30 Pro:\内部存储设备'
    for dername, sub, filenames in os.walk(path):
        print(dername, sub, filenames)