import gpiozero
import time

# rgb led
led = gpiozero.RGBLED(24, 23, 22)

def red():
    led.color = (1, 0, 0)

def green():
    led.color = (0, 1, 0)

def blue():
    led.color = (0, 0, 1)

def off():
    led.off()

def blink():
    led.blink(on_time=0.4, off_time=0.4, on_color=(1,0,0), n=3)