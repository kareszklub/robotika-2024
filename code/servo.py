from machine import Pin, PWM
from math import pi

class Servo:
	_p: PWM

	def __init__(self, p: Pin):
		self._p = PWM(p, freq=50)

	def deg(self, d: float):
		d = (d % 360) / 360
		self._p.duty_ns(int((1 + d) * 1_000_000))

	def rad(self, d: float):
		d = (d + 0.5 * pi) % (2 * pi) / (2 * pi)
		self._p.duty_ns(int((1 + d) * 1_000_000))

	def off(self):
		self._p.duty_u16(0)
