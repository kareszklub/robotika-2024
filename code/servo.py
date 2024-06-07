from machine import Pin, PWM
from utils import clamp
from math import pi

class Servo:
	_p: PWM

	_min: int
	_max: int

	def __init__(self, p: Pin, min_duty=1_000_000, max_duty=1_000_000):
		self._p = PWM(p, freq=50)
		self._min = min_duty
		self._max = max_duty

	def duty(self, d: float):
		d = clamp(d, 0, 1)

		duty = self._min + int((self._max - self._min) * d)
		print(f'servo to {d} (deg), {duty=}')
		self._p.duty_ns(duty)

	def deg(self, d: float):
		d = (d + 90) / 180
		self.duty(d)

	def rad(self, d: float):
		d = (d + 0.5 * pi) / pi
		self.duty(d)

	def off(self):
		self._p.duty_u16(0)