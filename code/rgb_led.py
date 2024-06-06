from machine import Pin, PWM

class RgbLed:
	_r: PWM
	_g: PWM
	_b: PWM

	def __init__(self, r: PWM, g: PWM, b: PWM):
		self._r = r
		self._g = g
		self._b = b

	def set_freq(self, freq: int):
		self._r.freq(freq)
		self._g.freq(freq)
		self._b.freq(freq)

	def color(self, r: float, g: float, b: float):
		self._r.duty_u16(int(0xffff - r * 0xffff))
		self._g.duty_u16(int(0xffff - g * 0xffff))
		self._b.duty_u16(int(0xffff - b * 0xffff))

	def off(self):
		self._r.duty_u16(0xffff)
		self._g.duty_u16(0xffff)
		self._b.duty_u16(0xffff)
