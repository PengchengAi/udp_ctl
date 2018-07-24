import os
from socket import *
# import matplotlib
# matplotlib.use("Agg")

import matplotlib.pyplot as plt


host_rx = ""
port = 13141

addr_rx = (host_rx, port)

udpServer = socket(AF_INET, SOCK_DGRAM)
udpServer.bind(addr_rx)

bufsize = 1024

cache_size = 1024
refresh_size = 16
refresh = 0
data_list = []

filepath = "/tmp/iic_data"
if not os.path.exists(filepath):
    os.mkdir(filepath)

plt.show()

while True:
    data, addr_r = udpServer.recvfrom(bufsize)
    if len(data_list) < cache_size:
        data_list.append(int(data)/0x2000000)
    else:
        data_list.append(int(data)/0x2000000)
        data_list.pop(0)
        refresh += 1
        if refresh == refresh_size:
            x = list(range(cache_size))
            plt.cla()
            plt.title("waveform")
            plt.ylim(0.7545, 0.7555)
            plt.plot(x, data_list)
            plt.pause(0.001)
            # plt.savefig(os.path.join(filepath, "wave.png"))
            print("renew figure")
            refresh = 0

    
