from machine import Pin, PWM

class HBridge:
	_mot_r_pwm: PWM
	_mot_l_pwm: PWM

	_mot_l_1: Pin
	_mot_l_2: Pin

	_mot_r_1: Pin
	_mot_r_2: Pin

	def __init__(self,
		mot_r_pwm: PWM, mot_l_pwm: PWM,
		mot_l_1: Pin, mot_l_2: Pin,
		mot_r_1: Pin, mot_r_2: Pin):		
		self._mot_r_pwm = mot_r_pwm
		self._mot_l_pwm = mot_l_pwm
		self._mot_l_1 = mot_l_1
		self._mot_l_2 = mot_l_2
		self._mot_r_1 = mot_r_1
		self._mot_r_2 = mot_r_2

	def drive(self, l: float, r: float):
		self._mot_l_1.value(l > 0)
		self._mot_l_2.value(l < 0)
		self._mot_l_pwm.duty_u16(abs(l) * 0xffff)

		self._mot_r_1.value(l > 0)
		self._mot_r_2.value(l < 0)
		self._mot_r_pwm.duty_u16(abs(r) * 0xffff)

	def brake(self):
		self._mot_r_1.value(True)
		self._mot_r_2.value(True)
		self._mot_r_1.value(True)
		self._mot_r_2.value(True)
		self._mot_l_pwm.duty_u16(0xffff)
		self._mot_r_pwm.duty_u16(0xffff)
