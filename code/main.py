from machine import Pin, PWM, I2C
from time import sleep_ms
import json

from ultra_sensor import UltraSensor
from rgb_sensor import RgbSensor
from h_bridge import HBridge
from rgb_led import RgbLed
from buzzer import Buzzer
from servo import Servo

from utils import rgb_rel

print("starting up")

with open('config.json') as f:
    cfg = json.load(f)

rgb_led = RgbLed(
    Pin(cfg['rgb_led']['r'], Pin.OUT),
    Pin(cfg['rgb_led']['g'], Pin.OUT),
    Pin(cfg['rgb_led']['b'], Pin.OUT)
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
        if cfg['rgb_sensor']['int'] else None,

    integration_time=cfg['rgb_sensor']['integration_time'],
    gain=cfg['rgb_sensor']['gain']
)

rgb_sensor.set_led(True)

ultra_sensor = UltraSensor(
    Pin(cfg['ultra_sensor']['trig'], Pin.OUT),
    Pin(cfg['ultra_sensor']['echo'], Pin.IN)
)

servo = Servo(
    Pin(cfg['servo']['pin'], Pin.OUT),

    cfg['servo']['freq'],

    cfg['servo']['min_duty'],
    cfg['servo']['max_duty']
)

h_bridge = HBridge(
    Pin(cfg['h_bridge']['pwm_l'],  Pin.OUT),
    Pin(cfg['h_bridge']['pwm_r'],  Pin.OUT),
    Pin(cfg['h_bridge']['in_l_1'], Pin.OUT),
    Pin(cfg['h_bridge']['in_l_2'], Pin.OUT),
    Pin(cfg['h_bridge']['in_r_1'], Pin.OUT),
    Pin(cfg['h_bridge']['in_r_2'], Pin.OUT),

    cfg['h_bridge']['freq']
)

buzzer = Buzzer(
    Pin(cfg['buzzer']['pin'], Pin.OUT),
    freq=cfg['buzzer']['freq']
)

led_builtin = Pin("LED", Pin.OUT)

print("done with initalization")

i = 0
secs = 3

while i < secs * 5:
    dist = ultra_sensor.measure_sync()
    col = rgb_rel(*rgb_sensor.get_data())

    rgb_led.set_color(*col)

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
