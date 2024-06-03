from time import sleep, time_ns
from machine import Pin, I2C
import struct

RGB_SENSOR_I2C_BASE_REG = 0x16
RGB_SENSOR_ADDRESS = 0x29
RGB_SENSOR_COMMAND_BIT = 0x80

sensors = {
    'ultra': None,
    'rgb': None,
    'imu': {
        'acceleration': None,
        'orientation': None
    }
}

led_builtin = Pin("LED", Pin.OUT)

trig = Pin(16, Pin.OUT)
echo = Pin(17, Pin.IN)

print("starting up")

rgb_selsor_i2c = I2C(1, scl=Pin(15), sda=Pin(14))
rgb_selsor_i2c.writeto_mem(RGB_SENSOR_ADDRESS, RGB_SENSOR_COMMAND_BIT | 0x0, bytes([0x1]))
sleep(0.010)
rgb_selsor_i2c.writeto_mem(RGB_SENSOR_ADDRESS, RGB_SENSOR_COMMAND_BIT | 0x0, bytes([0x1 | 0x2]))

def get_dist_sync():
    trig.on()
    sleep(0.00001)
    trig.off()

    while not echo.value():
        pass

    start = time_ns()
    while echo.value():
        pass
    duration = (time_ns() - start) / 1000

    cm = duration / 29 / 2
 
    if cm > 300:
        return -1
 
    return cm

def get_rgb_sync():
    color_bytes = rgb_selsor_i2c.readfrom_mem(RGB_SENSOR_ADDRESS, RGB_SENSOR_COMMAND_BIT | RGB_SENSOR_I2C_BASE_REG, 3 * 2)
    return struct.unpack('<HHH', color_bytes)

while True:
    dist = get_dist_sync()
    col = get_rgb_sync()

    print(f'distance = {dist}cm')
    print(f'color = {col}')

    led_builtin.toggle()
    sleep(0.1)


# led_rgb_r = Pin(13, Pin.OUT)
# led_rgb_g = Pin(12, Pin.OUT)
# led_rgb_b = Pin(11, Pin.OUT)
# 
# led_rgb_g.on()

# mot_r_pwm = Pin(0, Pin.OUT)
# mot_l_pwm = Pin(1, Pin.OUT)
# 
# mot_l_1 = Pin(14, Pin.OUT)
# mot_l_2 = Pin(15, Pin.OUT)
# 
# mot_r_1 = Pin(17, Pin.OUT)
# mot_r_2 = Pin(16, Pin.OUT)
# 
# mot_l_pwm.on()
# mot_r_pwm.on()
# 
# mot_r_1.on()
# mot_l_2.on()
