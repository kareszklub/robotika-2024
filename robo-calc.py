#!/bin/env python3
from math import pi

try:
	wheel_diameter = int(input('wheel diameter (40mm): '))
except:
	wheel_diameter = 40
wheel_diameter /= 1000
wheel_radius = wheel_diameter * 0.5

try:
	motor_torque = int(input('motor torque (8mNm): '))
except:
	motor_torque = 8
motor_torque /= 1000

try:
	motor_rpm = int(input('motor rpm (200): '))
except:
	motor_rpm = 200
motor_rps = motor_rpm / 60

try:
	motors = int(input('motor count (2): '))
except:
	motors = 2

try:
	weight = int(input('weight (500g): '))
except:
	weight = 500
weight /= 1000

print(f'robot params: {wheel_diameter=}cm {motor_torque=}mNm {motor_rpm=} {motors=} {weight=}g')

motor_force = motors * motor_torque / wheel_radius
acceleration = motor_force / weight
top_speed = motor_rps * wheel_diameter * pi

to_top_speed = top_speed / acceleration

print(f'{top_speed=} m/s')
print(f'{acceleration=} m/s^2')
print(f'{to_top_speed=} s')
