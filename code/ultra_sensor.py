from time import sleep_us, time_ns
from machine import Pin

class UltraSensor:
    _trig: Pin
    _echo: Pin

    def __init__(self, trig: Pin, echo: Pin):
        self._trig = trig
        self._echo = echo

    def measure_sync(self) -> float | None:
        self._trig.value(True)
        sleep_us(10)
        self._trig.value(False)

        while not self._echo.value():
            pass

        start = time_ns()
        diff = 0

        while self._echo.value() and diff < 60_000_000:
            diff = time_ns() - start
        duration = diff / 1000

        cm = duration / 29 / 2
    
        if cm > 300:
            return None

        return cm
