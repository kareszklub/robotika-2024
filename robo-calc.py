#!/bin/env python3
from typing import Callable
from math import pi

def get_param[T](name: str, unit: str, ty: Callable[[str], T], default: T) -> T:
	try:
		ty(input(f'{name} ({default}{unit}): '))
	except Exception:
		pass
	except KeyboardInterrupt:
		print()
		exit(0)

	return default

wheel_diameter = get_param('wheel diameter', 'mm',   float, 40)  / 1000
motor_torque   = get_param('motor torque',   'mNm',  float, 8)   / 1000
motor_rpm      = get_param('motor rpm',      '/60s', float, 200)
motors         = get_param('motor count',    '',     int,   2)
weight         = get_param('weight',         'g',    float, 500) / 1000

wheel_radius = wheel_diameter / 2
motor_rps = motor_rpm / 60

print(f'robot params: {wheel_diameter=}cm {motor_torque=}mNm {motor_rpm=} {motors=} {weight=}g')

motor_force = motors * motor_torque / wheel_radius
acceleration = motor_force / weight
top_speed = motor_rps * wheel_diameter * pi

to_top_speed = top_speed / acceleration

print(f'{top_speed=} m/s')
print(f'{acceleration=} m/s^2')
print(f'{to_top_speed=} s')
