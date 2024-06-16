from machine import PWM, Pin

class Buzzer:
	_p: PWM

	def __init__(self, p: Pin, freq: int = 2000):
		self._p = PWM(p, freq)

		# print(f'buzzer:\n\t{self._p}')

	def set_freq(self, freq: int):
		self._p.freq(freq)

	def set_volume(self, v: float):
		self._p.duty_u16(int(v * 0x7fff))

	def off(self):
		self._p.deinit()

'''
for i in range(1, 1000):
	v = i * 0.001
	print(v)
	buzzer.set_volume(v)
	sleep_ms(1)

buzzer.set_volume(0)
'''