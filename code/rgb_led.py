from machine import Pin, PWM

class RgbLed:
	_r: PWM
	_g: PWM
	_b: PWM

	def __init__(self, r: Pin, g: Pin, b: Pin, freq: int = 2000):
		self._r = PWM(r, freq=freq)
		self._g = PWM(g, freq=freq)
		self._b = PWM(b, freq=freq)

		# print(f'led:\n\t{self._r}\n\t{self._g}\n\t{self._b}')

	def set_color(self, r: float, g: float, b: float):
		self._r.duty_u16(int(0xffff - r * 0xffff))
		self._g.duty_u16(int(0xffff - g * 0xffff))
		self._b.duty_u16(int(0xffff - b * 0xffff))

	def set_freq(self, freq: int):
		self._r.freq(freq)
		self._g.freq(freq)
		self._b.freq(freq)

	def off(self):
		self._r.duty_u16(0xffff)
		self._g.duty_u16(0xffff)
		self._b.duty_u16(0xffff)
