from time import sleep, time_ns
from machine import Pin, I2C
import rgb_sensor

print("starting up")

rgb_sens = rgb_sensor.RgbSensor(I2C(0, scl=Pin(17), sda=Pin(16)), led_pin=Pin(18, Pin.OUT))
rgb_sens.setIntegrationTime(100)
rgb_sens.setGain(2)
rgb_sens.setLed(True)

# sensors = {
#     'ultra': None,
#     'rgb': None,
#     'imu': {
#         'acceleration': None,
#         'orientation': None
#     }
# }

led_builtin = Pin("LED", Pin.OUT)

def get_rgb_sync() -> tuple[int, int, int]:
    c, r, g, b = rgb_sens.getData()
    if c == 0:
        return 0, 0, 0
    return int(0xff * (r / c)), int(0xff * (g / c)), int(0xff * (b / c))

i = 0
while True:
    # dist = get_dist_sync()
    col = get_rgb_sync()

    # print(f'distance = {dist}cm')
    print(f'color = {col}')

    print(i)
    i += 1

    led_builtin.toggle()
    sleep(0.2)
