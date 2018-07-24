import smbus
import time
import os
from socket import *
import signal
import json
from gpiozero import LED, Button

btn = [Button(21), Button(20)]
output = [LED(16), LED(12), LED(7), LED(8), LED(25), LED(24)]

# device 1
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

host = "192.168.1.9"
port = 13141
addr_udp = (host, port)
udpClient = socket(AF_INET, SOCK_DGRAM)

class AlarmException(Exception):
    pass

def alarmHandler(signum, frame):
    raise AlarmException

base_addr = 0x00

def train_routine(classes, repeats):
    c = 1
    r = 1

    vectors = {}
    for i in range(classes):
        vectors["c%d" % (i+1)] = []

    print("class %d, turn %d" % (c, r))
    # wait some time
    time.sleep(0.3)

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

            data_t = str("z%d" % (i)) + str(data)
            udpClient.sendto(data_t, addr_udp)

        signal.signal(signal.SIGALRM, alarmHandler)
        signal.setitimer(signal.ITIMER_REAL, 0.01)
        try:
            while True:
                if btn[0].is_pressed:
                    break
                elif btn[1].is_pressed:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    return False
                time.sleep(0.001)
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
            # wait some time
            time.sleep(0.3)

        except AlarmException:
            # print("no hit")
            pass

    print(vectors)
    with open("i2c_param.json", "w") as f:
        json.dump(vectors, f, indent=4, sort_keys=True)

    print("finish training")
    return True

def val_routine():
    thresh = 2

    with open("i2c_param.json", "r") as f:
        vectors = json.load(f)

    print(vectors)

    def l2_distance(x, y):
        assert len(x) == len(y)
        assert len(x) == 8
        result = 0
        result += (x[0]-y[0]) * (x[0]-y[0]) * 0.25
        result += (x[1]-y[1]) * (x[1]-y[1]) * 0.25
        result += (x[2]-y[2]) * (x[2]-y[2]) * 0.5
        result += (x[3]-y[3]) * (x[3]-y[3]) * 0.5
        result += (x[4]-y[4]) * (x[4]-y[4]) * 0.5
        result += (x[5]-y[5]) * (x[5]-y[5])
        result += (x[6]-y[6]) * (x[6]-y[6])
        result += (x[7]-y[7]) * (x[7]-y[7])
        return result

    print("start testing")

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

            data_t = str("z%d" % (i)) + str(data)
            udpClient.sendto(data_t, addr_udp)

        signal.signal(signal.SIGALRM, alarmHandler)
        signal.setitimer(signal.ITIMER_REAL, 0.01)
        try:
            while True:
                if btn[0].is_pressed:
                    break
                elif btn[1].is_pressed:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    return False
                time.sleep(0.001)
            signal.setitimer(signal.ITIMER_REAL, 0)
            print("test result:")
            eval_list = []
            for key in vectors.keys():
                for item in vectors[key]:
                    l2 = l2_distance(data_list, item)
                    eval_list.append([key, l2])
            eval_list = sorted(eval_list, key=lambda x:x[1])
            print(eval_list)
            count = [0] * len(vectors.keys())
            for item in eval_list:
                num = int(item[0][1:]) - 1
                count[num] += 1
                if count[num] >= thresh:
                    print("the class is c%d" % (num + 1))
                    for elem in output:
                        elem.off()
                    output[num].on()
                    break
            # wait some time
            time.sleep(0.3)

        except AlarmException:
            # print("no hit")
            pass
    
    return True

if __name__ == "__main__":
    # startup
    function = None
    while True:
        print("------start up-------")
        time.sleep(0.3)

        # different functions
        while True:
            if btn[0].is_pressed:
                print("press key0, enter caiquan")
                function = 0
                break
            elif btn[1].is_pressed:
                print("press key1, enter huaquan")
                function = 1
                break
            time.sleep(0.1)
        
        time.sleep(0.5)
        print("-----enter training-----")

        if function == 0:
            ret = train_routine(4, 3)
        elif function == 1:
            ret = train_routine(6, 3)
        else:
            ret = False

        if ret == False:
            function = None
            continue

        time.sleep(0.5)
        print("-----enter testing-----")

        for elem in output:
            elem.off()

        val_routine()

        for elem in output:
            elem.off()

        function = None
