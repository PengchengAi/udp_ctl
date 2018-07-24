from gpiozero import LED, Button
import time

btn = Button(21)
led = LED(20)

while True:
    if btn.is_pressed:
        print("is pressed, led on")
        led.on()
    else:
        print("is released, led off")
        led.off()
    time.sleep(1)
