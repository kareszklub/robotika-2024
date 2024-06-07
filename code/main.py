from machine import Pin, PWM, I2C
from time import sleep_ms
import json

from ultra_sensor import UltraSensor
from rgb_sensor import RgbSensor
from h_bridge import HBridge
from rgb_led import RgbLed
from buzzer import Buzzer
from servo import Servo

print("starting up")

with open('config.json') as f:
    cfg = json.load(f)

rgb_led = RgbLed(
    Pin(cfg['rgb_led']['r']),
    Pin(cfg['rgb_led']['g']),
    Pin(cfg['rgb_led']['b'])
)

rgb_sensor = RgbSensor(
    I2C(
        cfg['rgb_sensor']['i2c_chan'],
        scl=Pin(cfg['rgb_sensor']['scl']),
        sda=Pin(cfg['rgb_sensor']['sda'])
    ),
    led_pin=Pin(cfg['rgb_sensor']['led'], Pin.OUT)
        if cfg['rgb_sensor']['led'] else None,
    interrupt_pin=Pin(cfg['rgb_sensor']['int'], Pin.OUT)
        if cfg['rgb_sensor']['int'] else None
)

if cfg['rgb_sensor']['integration_time']:
    rgb_sensor.set_integration_time(cfg['rgb_sensor']['integration_time'])
if cfg['rgb_sensor']['gain']:
    rgb_sensor.set_gain(cfg['rgb_sensor']['gain'])

rgb_sensor.set_led(True)

ultra_sensor = UltraSensor(
    Pin(cfg['ultra_sensor']['trig'], Pin.OUT),
    Pin(cfg['ultra_sensor']['echo'], Pin.IN)
)

servo = Servo(Pin(cfg['servo']['pin']))

led_builtin = Pin("LED", Pin.OUT)

print("done with initalization")

def get_rgb_sync() -> tuple[float, float, float]:
    c, r, g, b = rgb_sensor.get_data()
    # print(f'raw = {(c, r, g, b)}')
    if c == 0:
        return 0, 0, 0
    return r / c, g / c, b / c

i = 0
secs = 15

while i < secs * 5:
    dist = ultra_sensor.measure_sync()
    col = get_rgb_sync()

    rgb_led.color(*col)

    col = (int(0xff * col[0]), int(0xff * col[1]), int(0xff * col[2]))
    print(f'{i};{col};{dist}')

    i += 1
    led_builtin.toggle()
    sleep_ms(100)

rgb_sensor.set_led(False)
rgb_led.off()

print('done')

# while True:
#     led_builtin.toggle()
#     sleep_ms(1000)
