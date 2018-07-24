import os
from socket import *
# import matplotlib
# matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

host_rx = ""
port = 13141

addr_rx = (host_rx, port)

udpServer = socket(AF_INET, SOCK_DGRAM)
udpServer.bind(addr_rx)

bufsize = 1024

cache_size = 1024
refresh_size = 64
refresh = 0

multi = 4
sub = 220

data_list = []
for i in range(multi):
    data_list.append([])

data = [0.0] * multi
mean = [0.0] * multi
full = [False] * multi

autoscale = True
ylim = [(0.7545, 0.7555), (0.7721, 0.7731), (0.7808, 0.7818), (0.7615, 0.7625)]

plt.show()

color = ["r", "g", "b", "m"]

def decode_recv(recv):
    s = recv.decode()
    if s[0] != "z":
        return (None, None)
    else:
        # print(int(s[1]), int(s[2:])/0x2000000)
        return (int(s[1]), int(s[2:]))

while True:
    recv, addr_r = udpServer.recvfrom(bufsize)
    ind, data = decode_recv(recv)

    if ind is None:
        print("format error")
        continue

    if len(data_list[ind]) < cache_size:
        data_list[ind].append(int(data)/0x2000000)
    else:
        full[ind] = True
        data_list[ind].append(int(data)/0x2000000)
        data_list[ind].pop(0)

    if all(full):
        refresh += 1

    if refresh == refresh_size:
        x = list(range(cache_size))
        for i in range(multi):
            plt.subplot(sub+i+1)
            plt.cla()
            if autoscale:
                mean[i] = np.mean(data_list[i][-256:])
                plt.ylim((mean[i]-0.0005, mean[i]+0.0005))
            else:
                plt.ylim(ylim[i])
            plt.plot(x, data_list[i], color=color[i])
        plt.pause(0.0001)

        print("renew figure")
        refresh = 0



