from machine import Pin, PWM

class HBridge:
	_mot_r_pwm: PWM
	_mot_l_pwm: PWM

	_mot_l_1: Pin
	_mot_l_2: Pin

	_mot_r_1: Pin
	_mot_r_2: Pin

	def __init__(self,
		mot_l_pwm: Pin, mot_r_pwm: Pin,
		mot_l_1: Pin, mot_l_2: Pin,
		mot_r_1: Pin, mot_r_2: Pin,
		freq: int = 2000):
		self._mot_r_pwm = PWM(mot_r_pwm, freq=freq)
		self._mot_l_pwm = PWM(mot_l_pwm, freq=freq)
		self._mot_l_1 = mot_l_1
		self._mot_l_2 = mot_l_2
		self._mot_r_1 = mot_r_1
		self._mot_r_2 = mot_r_2

	def drive(self, l: float, r: float):
		self._mot_l_1.value(l > 0)
		self._mot_l_2.value(l < 0)
		self._mot_l_pwm.duty_u16(int(abs(l) * 0xffff))

		self._mot_r_1.value(r > 0)
		self._mot_r_2.value(r < 0)
		self._mot_r_pwm.duty_u16(int(abs(r) * 0xffff))

	def brake(self):
		self._mot_r_1.value(True)
		self._mot_r_2.value(True)
		self._mot_r_1.value(True)
		self._mot_r_2.value(True)
		self._mot_l_pwm.duty_u16(0xffff)
		self._mot_r_pwm.duty_u16(0xffff)

	def set_freq(self, freq: int):
		self._mot_l_pwm.freq(freq)
		self._mot_r_pwm.freq(freq)
