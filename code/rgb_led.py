from machine import Pin, PWM

led_rgb_r = Pin(13, Pin.OUT)
led_rgb_g = Pin(12, Pin.OUT)
led_rgb_b = Pin(11, Pin.OUT)

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

	def color(self, r: int, g: int, b: int):
		self._r.duty_u16(r * 0xff)
		self._g.duty_u16(g * 0xff)
		self._b.duty_u16(b * 0xff)

	def off(self):
		self._r.deinit()
		self._g.deinit()
		self._b.deinit()
