from ultra_sensor import UltraSensor
from utils import hsv_to_rgb
from h_bridge import HBridge
from rgb_led import RgbLed
from buzzer import Buzzer
from time import sleep_ms
from servo import Servo
from pid import PID

from debug import dprint, define_controls, recv_change
from networking import setup_wifi, setup_dbg
from time import ticks_ms, ticks_diff
from machine import Pin, reset
from dbg_magic import DbgNum
import micropython
import math

@micropython.native
def main():
    setup_wifi()
    setup_dbg()

    dprint('builtin led')
    l = Pin('LED', Pin.OUT)
    l.value(False)

    dprint('reset button')
    bt = Pin(0, Pin.IN, Pin.PULL_UP)
    bt.irq(lambda _: reset())

    dprint('rgb led')
    rgb_led = RgbLed(Pin(16, Pin.OUT), Pin(15, Pin.OUT), Pin(14, Pin.OUT))
    rgb_led.off()

    dprint('buzzer')
    buzzer = Buzzer(Pin(4, Pin.OUT))
    buzzer.set_freq(1000)
    buzzer.off()

    dprint('servo')
    s = Servo(Pin(22, Pin.OUT), min_duty=550_000, mid_duty=1_400_000, max_duty=2_390_000)
    s.deg(0)

    dprint('h bridge')
    hb = HBridge(
        Pin(9,  Pin.OUT), Pin(18, Pin.OUT),
        Pin(12, Pin.OUT), Pin(13, Pin.OUT),
        Pin(10, Pin.OUT), Pin(11, Pin.OUT)
    )
    hb.off()

    @micropython.native
    def test_stuffe():
        dprint('test stuffe')

        ##
        sleep_ms(1000)
        ##

        for _ in range(10):
            l.toggle()
            sleep_ms(100)

        l.toggle()

        ##
        sleep_ms(1000)
        ##

        for i in range(1000):
            rgb_led.set_color(*hsv_to_rgb(i * 0.36, 1, 0.75))
            sleep_ms(2)

        sleep_ms(500)
        rgb_led.set_color(0, 0, 0)

        ##
        sleep_ms(1000)
        ##

        for i in range(1000):
            buzzer.set_volume(i * 0.001)
            sleep_ms(1)

        buzzer.set_volume(1)
        sleep_ms(1000)

        for i in range(1000):
            buzzer.set_volume(1 - i * 0.001)
            sleep_ms(1)
        buzzer.set_volume(0)

        ##
        sleep_ms(1000)
        ##

        s.duty(0)
        sleep_ms(200)

        for i in range(1000):
            s.duty(i * 0.001)
            sleep_ms(3)

        for i in range(1000):
            s.duty(1 - i * 0.001)
            sleep_ms(3)

        s.deg(0)

        ##
        sleep_ms(1000)
        ##

        for i in range(1000):
            j = i * 0.001
            hb.drive(j, j)
            sleep_ms(2)

        hb.drive(1, 1)
        sleep_ms(1000)

        for i in range(1000):
            j = 1 - i * 0.001
            hb.drive(j, j)
            sleep_ms(2)

        hb.off()

    @micropython.native
    def pid_wall():
        ctrls = {
            'P': { 'val': DbgNum(0.0), 'min': 0.0, 'max': 20.0, },
            'I': { 'val': DbgNum(0.0), 'min': 0.0, 'max': 20.0, },
            'D': { 'val': DbgNum(0.0), 'min': 0.0, 'max': 20.0, },

            'IMin': { 'val': DbgNum(-2.0), 'min': -2.0, 'max': 2.0, },
            'IMax': { 'val': DbgNum( 2.0), 'min': -2.0, 'max': 2.0, },

            'dt': { 'val': DbgNum(0), 'min': 0, 'max': 100, },

            'speed offset': { 'val': DbgNum(0.5), 'min': 0.0, 'max': 1.0, },
        }
        define_controls(ctrls)

        dprint('PID wall')

        for i in range(10):
            if i % 2 == 0:
                rgb_led.set_color(1, 0, 0)
            else:
                rgb_led.set_color(0, 0, 0)

            sleep_ms(300)

        sleep_ms(5000)

        ultra_sensor = UltraSensor(Pin(20, Pin.OUT), Pin(19, Pin.IN))

        pid = PID(
            0.15,
            3, 0, 0,
            -0.75, 0.75
        )
        dt_ms = 10
        dt_over = 0

        secs = const(10)
        speed_offset = const(0.5)

        rgb_led.set_color(1, 0.65, 0)

        @micropython.native
        def run():
            return ticks_diff(ticks_ms(), loop_start) < secs * 1000
        break_out = False

        loop_start = ticks_ms()
        while run():
            inner_start = ticks_ms()

            recv_change(ctrls)

            dist = None
            while dist is None:
                dist = ultra_sensor.measure_sync()
                if not run():
                    break_out = True
                    break

            if break_out:
                break

            o = (1 - speed_offset) * -pid.compute(dist, 0.001 * (dt_ms + dt_over))
            o += math.copysign(speed_offset, o)

            if abs(o) > 1:
                buzzer.set_volume(1)
            else:
                buzzer.off()

            dprint(f'{dist=} {o=}')
            hb.drive(o, o)

            dt = int(dt_ms - ticks_diff(ticks_ms(), inner_start))
            if dt > 0:
                sleep_ms(dt_ms)
            else:
                dt_over = -dt
                dprint(f'{dt_over=}')

        hb.off()
        rgb_led.set_color(0, 1, 0)

    @micropython.native
    def pid_line():
        dprint('PID line')

        pid = PID(0.5, 1, 1, 1, 0.4, 0.4)
        for _ in range(300):
            rgb = rgb_rel(*rgb.get_data())
            rgb_led.set_color(*rgb)

            _h, _s, v = rgb_to_hsv(*rgb)

            d = pid.compute(v, 0.020)
            h_bridge.drive(0.75 + d, 0.75 - d)

            sleep_ms(20)

    # test_stuffe()
    pid_wall()
    # pid_line()

    dprint('done')

if __name__ == '__main__':
    main()
