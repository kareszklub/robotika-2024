from _thread import start_new_thread
from time import sleep_ms
from machine import Pin

from sensor_thread import sensor_thread_main, Sensors
from h_bridge import HBridge
from rgb_led import RgbLed
from buzzer import Buzzer
from servo import Servo

from utils import rgb_rel

from networking import robot_id
from config import cfg

def main():
    print("starting up")

    sensor_data = Sensors()
    start_new_thread(sensor_thread_main, (sensor_data))

    rgb_led = RgbLed(
        Pin(cfg['rgb_led']['r'], Pin.OUT),
        Pin(cfg['rgb_led']['g'], Pin.OUT),
        Pin(cfg['rgb_led']['b'], Pin.OUT)
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
        sensor_data.lock.acquire()
        dist = sensor_data.dist
        col = sensor_data.rgb
        sensor_data.lock.release()

        rgb_led.set_color(*col)

        col = (int(0xff * col[0]), int(0xff * col[1]), int(0xff * col[2]))
        print(f'{i};{col};{dist}')

        i += 1
        led_builtin.toggle()
        sleep_ms(100)

    print('done')

    sensor_data.sleep = True

    h_bridge.drive(0, 0)
    buzzer.off()
    servo.off()
    rgb_led.off()


if __name__ == '__main__':
    main()
