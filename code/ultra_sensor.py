from time import sleep, time_ns
from machine import Pin

trig = Pin(16, Pin.OUT)
echo = Pin(17, Pin.IN)

def get_dist_sync():
    trig.on()
    sleep(0.00001)
    trig.off()

    while not echo.value():
        pass

    start = time_ns()
    while echo.value():
        pass
    duration = (time_ns() - start) / 1000

    cm = duration / 29 / 2
 
    if cm > 300:
        return -1
 
    return cm
