from machine import Pin, time_pulse_us
from time import sleep_us
from array import array

M_PER_US = const(0.0001715)

MIN_DIST = const(0.02)
MAX_DIST = const(4.0)

class UltraSensor:
    _trig: Pin
    _echo: Pin

    _arr: array[float]
    _arr_len: int
    _arr_p: int

    def __init__(self, trig: Pin, echo: Pin, array_len: int = 5):
        self._arr = array('f', [])
        self._arr_len = array_len
        self._arr_p = 0

        self._trig = trig
        self._echo = echo

    def measure_sync(self) -> float | None:
        self._trig.value(True)
        sleep_us(15)
        self._trig.value(False)

        dur_us = time_pulse_us(self._echo, 1, 60_000)

        m = dur_us * M_PER_US
        if m < MIN_DIST or m > MAX_DIST:
            return None

        l = len(self._arr)
        if self._arr_len <= l:
            self._arr[self._arr_p] = m
            self._arr_p = (self._arr_p + 1) % self._arr_len
        else:
            self._arr.append(m)
            self._arr_p = 0

        return sum(self._arr[:self._arr_len]) / self._arr_len
