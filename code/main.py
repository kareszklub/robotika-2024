from ultra_sensor import UltraSensor
from rgb_sensor import RgbSensor
from h_bridge import HBridge
from rgb_led import RgbLed
from buzzer import Buzzer
from time import sleep_ms
from servo import Servo

from utils import hsv_to_rgb, rgb_rel, get_vsys, get_temperature
from debug import dprint, define_controls, recv_changes
from networking import setup_wifi, setup_dbg, socks
from machine import Pin, ADC, I2C, reset
from time import ticks_ms, ticks_diff
from collections import OrderedDict
from sys import print_exception
from dbg_magic import DbgVal
from config import cfg
from io import BytesIO
from pid import PID
import micropython
import math
import gc

class Robot:
    led: Pin
    reset: Pin

    rgb_led: RgbLed
    buzzer: Buzzer
    servo: Servo
    h_bridge: HBridge

    proximity_sensor: Pin
    ultra_sensor: UltraSensor
    rgb_sensor: RgbSensor

    on_ground: bool

    def init(self):
        dprint('builtin led')
        led = Pin('LED', Pin.OUT)
        led.value(True)
        self.led = led

        dprint('reset button')
        reset_bt = Pin(cfg['reset_button']['pin'], Pin.IN, Pin.PULL_UP)
        reset_bt.irq(lambda _: reset())
        self.reset = reset_bt

        dprint('rgb led')
        self.rgb_led = RgbLed(
            Pin(cfg['rgb_led']['r'], Pin.OUT),
            Pin(cfg['rgb_led']['g'], Pin.OUT),
            Pin(cfg['rgb_led']['b'], Pin.OUT),

            cfg['rgb_led']['freq']
        )

        dprint('buzzer')
        self.buzzer = Buzzer(
            Pin(cfg['buzzer']['pin'], Pin.OUT),
            freq=cfg['buzzer']['freq']
        )

        dprint('servo')
        self.servo = Servo(
            Pin(cfg['servo']['pin'], Pin.OUT),

            cfg['servo']['freq'],

            cfg['servo']['min_duty'],
            cfg['servo']['mid_duty'],
            cfg['servo']['max_duty']
        )

        dprint('h bridge')
        self.h_bridge = HBridge(
            Pin(cfg['h_bridge']['pwm_l'],  Pin.OUT),
            Pin(cfg['h_bridge']['pwm_r'],  Pin.OUT),
            Pin(cfg['h_bridge']['1A'], Pin.OUT),
            Pin(cfg['h_bridge']['2A'], Pin.OUT),
            Pin(cfg['h_bridge']['3A'], Pin.OUT),
            Pin(cfg['h_bridge']['4A'], Pin.OUT),

            cfg['h_bridge']['freq']
        )

        dprint('proximity sensor')
        proximity_sensor = Pin(cfg['proximity_sensor']['pin'], Pin.IN)
        proximity_sensor.irq(lambda p: setattr(self, 'on_ground', p.value()), hard=True)
        self.proximity_sensor = proximity_sensor
        self.on_ground = proximity_sensor.value()

        dprint('ultra sensor')
        self.ultra_sensor = UltraSensor(
            Pin(cfg['ultra_sensor']['trig'], Pin.OUT),
            Pin(cfg['ultra_sensor']['echo'], Pin.IN)
        )

        dprint('rgb sensor')
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
        self.rgb_sensor = rgb_sensor

        led.value(True)

def test_stuffe(r: Robot):
    dprint('test stuffe')

    ##
    sleep_ms(1000)
    ##

    for _ in range(10):
        r.led.toggle()
        sleep_ms(100)

    r.led.toggle()

    ##
    sleep_ms(1000)
    ##

    for i in range(1000):
        r.rgb_led.set_color(*hsv_to_rgb(i * 0.36, 1, 0.75))
        sleep_ms(2)

    sleep_ms(500)
    r.rgb_led.set_color(0, 0, 0)

    ##
    sleep_ms(1000)
    ##

    for i in range(1000):
        r.buzzer.set_volume(i * 0.001)
        sleep_ms(1)

    r.buzzer.set_volume(1)
    sleep_ms(1000)

    for i in range(1000):
        r.buzzer.set_volume(1 - i * 0.001)
        sleep_ms(1)
    r.buzzer.set_volume(0)

    ##
    sleep_ms(1000)
    ##

    r.servo.duty(0)
    sleep_ms(200)

    for i in range(1000):
        r.servo.duty(i * 0.001)
        sleep_ms(3)

    for i in range(1000):
        r.servo.duty(1 - i * 0.001)
        sleep_ms(3)

    r.servo.deg(0)

    ##
    sleep_ms(1000)
    ##

    for i in range(1000):
        j = i * 0.001
        r.h_bridge.drive(j, j)
        sleep_ms(2)

    r.h_bridge.drive(1, 1)
    sleep_ms(1000)

    for i in range(1000):
        j = 1 - i * 0.001
        r.h_bridge.drive(j, j)
        sleep_ms(2)

    r.h_bridge.off()

def pid_wall(r: Robot):
    dprint('PID wall')

    ctrls = OrderedDict([
        ('run', DbgVal(True)),

        ('side', DbgVal(False)),
        ('servo duty', DbgVal(0.5, 0, 1, call=lambda d: r.servo.duty(d))),

        ('sp', DbgVal(0.3, 0, 1.5)),

        ('P', DbgVal(0.0, 0, 50)), # 10
        ('I', DbgVal(0.0, 0, 50)), # 2
        ('D', DbgVal(0.0, 0, 50)), # 2

        ('II', DbgVal(1.0, 0.01, 100)), # 10

        ('dt', DbgVal(20, 1, 100)), # 15

        ('front speed offset', DbgVal(0.6, 0, 1)),
        ('side speed offset', DbgVal(0.7, 0, 1)),

        ('ultra avg len', DbgVal(3, 1, 30)),

        ('IMin', DbgVal(-0.05, -2, 2)),
        ('IMax', DbgVal( 0.05, -2, 2)),
    ])
    define_controls(ctrls)

    for i_print in range(6):
        if i_print % 2 == 0:
            r.rgb_led.set_color(1, 0, 0)
        else:
            r.rgb_led.set_color(0, 0, 0)

        sleep_ms(300)

    pid = PID(
        ctrls['sp'],
        ctrls['P'], ctrls['I'], ctrls['D'],
        ctrls['IMin'], ctrls['IMax']
    )

    r.ultra_sensor._arr_len = ctrls['ultra avg len']
    pid._integr_const = ctrls['II']

    front_speed_offset = ctrls['front speed offset']
    side_speed_offset = ctrls['side speed offset']

    servo_duty = ctrls['servo duty']
    r.servo.duty(servo_duty)

    side = ctrls['side']
    dt_ms = ctrls['dt']
    run = ctrls['run']

    dt_over = 0
    while run:
        inner_start = ticks_ms()

        recv_changes(ctrls)

        i_recv = 0
        dist = None
        while run and dist is None:
            dist = r.ultra_sensor.measure_sync()
            i_recv += 1

            if i_recv == 3:
                recv_changes(ctrls)
            elif i_recv == 5:
                gc.collect()
                i_recv = 0

        if not run:
            break

        dt_pid = 0.001 * (dt_ms + dt_over)
        o = -pid.compute(dist, dt_pid)

        if side:
            if servo_duty < 0.5:
                o = -o

            r.h_bridge.drive(side_speed_offset + o, side_speed_offset - o)
        else:
            if abs(o) <= 0.2:
                o = 0
            else:
                o = math.copysign(front_speed_offset, o) + (1 - front_speed_offset) * o

            r.h_bridge.drive(o, o)

        if abs(o) > 1:
            r.buzzer.set_volume(1)
        else:
            r.buzzer.off()

        col = rgb_rel(*r.rgb_sensor.get_data())
        r.rgb_led.set_color(*col)
        col = (int(0xff * col[0]), int(0xff * col[1]), int(0xff * col[2]))
        dprint(
            f'<span style="background:rgb{col};display:inline-block;' +
            'width:30px;height:15px;vertical-align:middle;"></span>' +
            f' dist={dist:.5f} I={pid._integr:+.3f} dt={dt_pid:.3f} o={o:.3f}'
        )

        gc.collect()
        dt = int(dt_ms - ticks_diff(ticks_ms(), inner_start))

        if dt > 0:
            sleep_ms(dt_ms)
        elif dt != 0:
            dt_over = -dt

    r.rgb_led.set_color(0, 1, 0)

def pid_line(r: Robot):
    dprint('PID line')

    pid = PID(0.5, 1, 1, 1, 0.4, 0.4)
    for _ in range(300):
        rgb = rgb_rel(*r.rgb_sensor.get_data())
        rgb_led.set_color(*rgb)

        _h, _s, v = rgb_to_hsv(*rgb)

        d = pid.compute(v, 0.020)
        r.h_bridge.drive(0.75 + d, 0.75 - d)

        sleep_ms(20)

def main():
    vsys = get_vsys()
    temp = get_temperature()

    r = Robot()
    r.init()

    r.h_bridge.off()
    r.rgb_led.off()
    r.buzzer.off()
    r.servo.off()

    setup_wifi()
    setup_dbg()

    dprint(f'starting.. {vsys=} {temp=}')
    try:
        # test_stuffe(r)
        pid_wall(r)
        # pid_line(r)

        dprint('done')
    except Exception as err:
        bio = BytesIO()
        print_exception(err, bio)
        dprint('<div style="color:red;">' + str(bio.getvalue(), 'utf-8') + '</div>')
        raise err
    except:
        pass
    finally:
        r.h_bridge.off()
        r.buzzer.off()
        r.servo.off()
        socks[0].close()        

if __name__ == '__main__':
    main()
