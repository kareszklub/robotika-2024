from time import sleep_us, ticks_us, ticks_diff
from _thread import LockType, allocate_lock
from machine import Pin, I2C, lightsleep
from utils import rgb_rel, rgb_to_hsv
from ultra_sensor import UltraSensor
from rgb_sensor import RgbSensor
from config import cfg

class Sensors:
    lock: LockType
    sleep: bool
    run: bool

    rgb: tuple[float, float, float]
    hsv: tuple[float, float, float]
    dist: float | None

    def __init__(self) -> None:
        self.lock = allocate_lock()

        self.run = True
        self.sleep = False

        self.rgb = 0, 0, 0
        self.hsv = 0, 0, 0
        self.dist = None

POLL_DELAY_US = const(100_000)

def sensor_thread_main(data: Sensors):
    rgb = RgbSensor(
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
    rgb.set_led(True)

    ultra = UltraSensor(
        Pin(cfg['ultra_sensor']['trig'], Pin.OUT),
        Pin(cfg['ultra_sensor']['echo'], Pin.IN)
    )

    while data.run:
        if data.sleep:
            rgb.set_led(False)
            lightsleep()
            rgb.set_led(True)

        start = ticks_us()

        raw_rgb = rgb.get_data()
        rel_rgb = rgb_rel(raw_rgb)

        data.lock.acquire()
        data.hsv = rgb_to_hsv(rel_rgb)
        data.dist = ultra.measure_sync()
        data.lock.release()

        t_diff = round(POLL_DELAY_US - ticks_diff(ticks_us(), start) / 1000)
        if t_diff > 0:
            sleep_us(t_diff)

    rgb.set_led(False)
