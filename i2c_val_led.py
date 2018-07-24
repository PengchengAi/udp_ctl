import smbus
import json
import signal
from gpiozero import LED
import time

bus = smbus.SMBus(1)

addr_0 = 0x2a
addr_1 = 0x2b

base_addr = 0x00

thresh = 2

with open("i2c_param.json", "r") as f:
    vectors = json.load(f)

print(vectors)

led = [LED(17), LED(27), LED(22)]
en = LED(10) # on(): enable. off(): disable.

led_mode = None
if len(vectors.keys()) == 4:
    led_mode = "xyz"
elif len(vectors.keys()) == 6:
    led_mode = "abcde"
else:
    led_mode = None

class AlarmException(Exception):
    pass

def alarmHandler(signum, frame):
    raise AlarmException

def light_led(mode, code):
    # background class
    if code is None:
        en.off()
        return
    # 3 gestures mode or 5 gestures mode
    if mode is None:
        return
    elif mode == "abcde":
        code = code + 3
    # light led:
    i = (code & 0x04) >> 2
    j = (code & 0x02) >> 1
    k = (code & 0x01)
    if k % 2:
        led[0].on()
    else:
        led[0].off()
    if j % 2:
        led[1].on()
    else:
        led[1].off()
    if i % 2:
        led[2].on()
    else:
        led[2].off()

    en.on()
    
def print_class(mode, num):
    if mode == "xyz":
        if num == 1:
            print("the class is stone")
        elif num == 2:
            print("the class is scissors")
        elif num == 3:
            print("the class is cloth")
    elif mode == "abcde":
        if num == 1:
            print("the class is one")
        elif num == 2:
            print("the class is two")
        elif num == 3:
            print("the class is three")
        elif num == 4:
            print("the class is four")
        elif num == 5:
            print("the class is five")
    else:
        return

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

cnt_class = [0] * len(vectors.keys())
num_class = 0

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
    eval_list = []
    for key in vectors.keys():
        for item in vectors[key]:
            l2 = l2_distance(data_list, item)
            eval_list.append([key, l2])
    eval_list = sorted(eval_list, key=lambda x:x[1])
    count = [0] * len(vectors.keys())
    for item in eval_list:
        num = int(item[0][1:]) - 1
        count[num] += 1
        if count[num] >= thresh:
            if num == 0:
                light_led(led_mode, None)
            else:
                cnt_class[num] += 1
                num_class = num
                light_led(led_mode, num - 1)
            break
    
    # display the class
    if cnt_class[num_class] >= 5:
        print(eval_list)
        print_class(led_mode, num_class)
        cnt_class = [0] * len(vectors.keys())
        num_class = 0
    
    # sleep some time
    time.sleep(0.05)
