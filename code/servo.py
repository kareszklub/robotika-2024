from machine import Pin, PWM
from utils import clamp
from math import pi

class Servo:
    _p: PWM

    _min: int
    _mid: int
    _max: int

    def __init__(self, p: Pin, freq: int = 50,
        min_duty: int = 1_000_000, mid_duty: int = 1_500_000, max_duty: int = 2_000_000):
        self._p = PWM(p, freq=freq)
        self._min = min_duty
        self._mid = mid_duty
        self._max = max_duty

    def duty(self, d: float):
        d = clamp(d, 0, 1)

        duty = (
            (self._min + int((self._mid - self._min) * d * 2)) if d <= 0.5
                    else (self._mid + int((self._max - self._mid) * (d * 2 - 1)))
        )

        self._p.duty_ns(duty)

    def deg(self, d: float):
        d = (d + 90) / 180
        self.duty(d)

    def rad(self, d: float):
        d = (d + 0.5 * pi) / pi
        self.duty(d)

    def off(self):
        self._p.deinit()
