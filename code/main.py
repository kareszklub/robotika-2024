from machine import Pin, PWM, I2C
from rgb_sensor import RgbSensor
from rgb_led import RgbLed
from time import sleep_ms

print("starting up")

rgbled = RgbLed(PWM(Pin(15)), PWM(Pin(13)), PWM(Pin(14)))
rgbled.set_freq(2000)

rgb_sens = RgbSensor(I2C(0, scl=Pin(17), sda=Pin(16)), led_pin=Pin(18, Pin.OUT))
rgb_sens.set_integration_time(40)
rgb_sens.set_gain(0b11)
rgb_sens.set_led(True)

led_builtin = Pin("LED", Pin.OUT)

def get_rgb_sync() -> tuple[int, int, int]:
    c, r, g, b = rgb_sens.get_data()
    print(f'raw = {(c, r, g, b)}')
    if c == 0:
        return 0, 0, 0
    return int(0xff * (r / c)), int(0xff * (g / c)), int(0xff * (b / c))

i = 0
secs = 15

while i < secs * 5:
    print(i, end=' ')
    i += 1

    # dist = get_dist_sync()
    col = get_rgb_sync()

    # print(f'distance = {dist}cm')
    print(f'color = {col}, grayscale = {rgb_to_grayscale(*col)}')
    rgbled.color(*col)

    led_builtin.toggle()
    sleep_ms(100)

rgb_sens.set_led(False)
led_builtin.off()
rgbled.off()

print('done')
