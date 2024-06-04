from time import sleep, time_ns
from machine import Pin, I2C
import rgb_sensor

print("starting up")

rgb_sens = rgb_sensor.RgbSensor(I2C(1, scl=Pin(15), sda=Pin(14)))

# sensors = {
#     'ultra': None,
#     'rgb': None,
#     'imu': {
#         'acceleration': None,
#         'orientation': None
#     }
# }

led_builtin = Pin("LED", Pin.OUT)

# def get_rgb_sync():
#     c, r, g, b = rgb_sens.getData()
#     return int(0xff * (r / c)), int(0xff * (g / c)), int(0xff * (b / c))

i = 0
while True:
    # dist = get_dist_sync()
    # col = get_rgb_sync()

    # print(f'distance = {dist}cm')
    # print(f'color = {col}')

    print(i)
    i += 1

    led_builtin.toggle()
    sleep(0.2)
