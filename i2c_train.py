import smbus
import time
import os
from socket import *
import signal
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("classes", type=int, help="how many classes to train")
args = parser.parse_args()

print(args.classes)

#device 1
bus = smbus.SMBus(1)

addr_0 = 0x2a
addr_1 = 0x2b

recount_th0 = [0x08, 0x09, 0x0a, 0x0b, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x19, 0x1b, 0x1e, 0x1f, 0x20, 0x21, 0x1a]
reg_data_th0 = [0x2983, 0x2983, 0x2983, 0x2983, 0x0a00, 0x0a00, 0x0a00, 0x0a00, 0x0220, 0x0220, 0x0220, 0x0220, 0x0000,
              0x0dc2, 0x007c, 0x007c, 0x007c, 0x007c, 0x0116]

for  i in range (19):
    bus.write_word_data(addr_0, recount_th0[i], reg_data_th0[i])

for  i in range (19):
    bus.write_word_data(addr_1, recount_th0[i], reg_data_th0[i])

# with the format[L[7:0],h[7:0]](high and low reverse)
for  i in range (19):
    data = bus.read_word_data(addr_0, recount_th0[i]) 
    print(hex(data))

for  i in range (19):
    data = bus.read_word_data(addr_1, recount_th0[i]) 
    print(hex(data))

# host = "192.168.1.9"
# port = 13141
# addr_udp = (host, port)
# udpClient = socket(AF_INET, SOCK_DGRAM)

class AlarmException(Exception):
    pass

def alarmHandler(signum, frame):
    raise AlarmException

base_addr = 0x00

classes = args.classes
repeats = 3

c = 1
r = 1

vectors = {}
for i in range(classes):
    vectors["c%d" % (i+1)] = []

print("class %d, turn %d" % (c, r))

while True:
    data_list = [0.0] * 8

    for i in range(8):
        if i < 4:
            data_h = bus.read_word_data(addr_0, base_addr + i*2)
            data_l = bus.read_word_data(addr_0, base_addr + i*2 + 1)
        else:
            data_h = bus.read_word_data(addr_1, base_addr + (i-4)*2)
            data_l = bus.read_word_data(addr_1, base_addr + (i-4)*2 + 1)

        data_h = ((data_h & 0xff) << 8) + ((data_h & 0xff00) >> 8)
        data_l = ((data_l & 0xff) << 8) + ((data_l & 0xff00) >> 8)

        data = data_h * 0x10000 + data_l

        data_list[i] = data
    
        # print(hex(data_h), hex(data_l), hex(data))

        # data_t = str("z%d" % (i)) + str(data)

        # udpClient.sendto(data_t, addr_udp)

    signal.signal(signal.SIGALRM, alarmHandler)
    signal.setitimer(signal.ITIMER_REAL, 0.01)
    try:
        text = raw_input("")
        signal.setitimer(signal.ITIMER_REAL, 0)
        print("save the vector")
        vectors["c%d" % (c)].append(data_list)
        r += 1
        if r > repeats:
            r = 1
            c += 1
            if c > classes:
                break
        
        print("class %d, turn %d" % (c, r))

    except AlarmException:
        # print("no hit")
        pass

print(vectors)
with open("i2c_param.json", "w") as f:
    json.dump(vectors, f, indent=4, sort_keys=True)

print("finish training")



