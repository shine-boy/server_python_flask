import os
import socket


class ARP:
    def get_ips(self):
        host=socket.gethostbyname(socket.gethostname())
        os.system("arp -a>ips_temp.txt")
        with open("ips_temp.txt") as fp:
            for line in fp:
                line=line.split()[:2]
                if line and line[0].startswith(host[:4]) and (not line[0].endswith("255")):
                    print(":".join(line))