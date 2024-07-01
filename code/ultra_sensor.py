from time import sleep_us, ticks_us, ticks_diff
from machine import Pin

CM_PER_US = const(1 / (343 * 1000))

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

        cycle_start = ticks_us()
        while not self._echo.value():
            if ticks_diff(ticks_us(), cycle_start) >= 60_000:
                return None

        start = ticks_us()
        while self._echo.value():
            if ticks_diff(ticks_us(), cycle_start) >= 60_000:
                return None

        dur_us = ticks_diff(ticks_us(), start)
        cm = dur_us * CM_PER_US
    
        return cm if cm <= 300 else None
