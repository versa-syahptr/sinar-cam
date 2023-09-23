import gpiozero
import atexit

# rgb led
led = gpiozero.RGBLED(24, 23, 22, active_high=False)

def red():
    led.color = (1, 0, 0)

def green():
    led.color = (0, 1, 0)

def blue():
    led.color = (0, 0, 1)

def off():
    led.off()

def blink(color_func=red):
    color_func()
    led.blink(on_time=0.4, off_time=0.4, on_color=led.color, n=3)

atexit.register(off)