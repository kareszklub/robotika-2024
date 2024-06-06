from machine import PWM

class Buzzer:
	_p: PWM

	def __init__(self, p: Pin):
		self._p = PWM(p, freq=2000)

	def set_freq(self, freq: int):
		self._p.freq(freq)

	def volume(self, v: float):
		self._p.duty_u16(int(v * 0xffff))

	def off(self):
		self._p.duty_u16(0xffff)
