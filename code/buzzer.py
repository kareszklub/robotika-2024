from machine import PWM, Pin

class Buzzer:
	_p: PWM

	def __init__(self, p: Pin, freq: int = 2000):
		self._p = PWM(p, freq)

	def set_freq(self, freq: int):
		self._p.freq(freq)

	def volume(self, v: float):
		self._p.duty_u16(int(v * 0xffff))

	def off(self):
		self._p.duty_u16(0xffff)
