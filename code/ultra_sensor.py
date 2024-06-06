from time import sleep, time_ns
from machine import Pin

class UltraSensor:
    _trig: Pin(16, Pin.OUT)
    _echo: Pin(17, Pin.IN)

    def __init__(self, trig: Pin, echo: Pin):
        self._trig = trig
        self._echo = echo

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
