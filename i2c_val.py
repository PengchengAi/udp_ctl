import smbus
import json
import signal

bus = smbus.SMBus(1)

addr_0 = 0x2a
addr_1 = 0x2b

base_addr = 0x00

thresh = 2

with open("i2c_param.json", "r") as f:
    vectors = json.load(f)

print(vectors)

class AlarmException(Exception):
    pass

def alarmHandler(signum, frame):
    raise AlarmException

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

    signal.signal(signal.SIGALRM, alarmHandler)
    signal.setitimer(signal.ITIMER_REAL, 0.01)
    try:
        text = raw_input("")
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
                break

    except AlarmException:
        # print("no hit")
        pass
