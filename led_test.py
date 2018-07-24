from gpiozero import LED
from time import sleep

led = [LED(17), LED(27), LED(22)]
en = LED(10) # on(): enable. off(): disable.

while True:
    for i in range(2):
        for j in range(2):
            for k in range(2):
                if i % 2:
                    led[2].on()
                else:
                    led[2].off()
                if j % 2:
                    led[1].on()
                else:
                    led[1].off()
                if k % 2:
                    led[0].on()
                else:
                    led[0].off()
                for _ in range(5):
                    en.on()
                    sleep(0.1)
                    en.off()
                    sleep(0.1)

