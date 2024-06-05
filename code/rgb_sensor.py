from machine import I2C, Pin
from time import sleep_ms
import struct

DEFAULT_ADDRESS = 0x29
CMD_BIT = 0x80

class Register:
    ENABLE  = 0x00
    ATIME   = 0x01
    WTIME   = 0x03
    AILTL   = 0x04
    AILTH   = 0x05
    AIHTL   = 0x06
    AIHTH   = 0x07
    PERS    = 0x0C
    CONFIG  = 0x0D
    CONTROL = 0x0F
    ID      = 0x12
    STATUS  = 0x13
    CDATAL  = 0x14
    CDATAH  = 0x15
    RDATAL  = 0x16
    RDATAH  = 0x17
    GDATAL  = 0x18
    GDATAH  = 0x19
    BDATAL  = 0x1A
    BDATAH  = 0x1B

PON  = 0x01
AEN  = 0x02
WEN  = 0x08
AIEN = 0x10

class RgbSensor:
    _addr: int
    _i2c: I2C

    _interrupt_pin: Pin
    _led_pin: Pin

    def __init__(self, i2c: I2C, addr = DEFAULT_ADDRESS, led_pin: Pin = None, interrupt_pin: Pin = None):
        self._interrupt_pin = interrupt_pin
        self._led_pin = led_pin
        self._addr = addr
        self._i2c = i2c

        self.write_bits(Register.ENABLE, PON, PON)
        sleep_ms(10)
        self.write_bits(Register.ENABLE, AEN, AEN)

    def write8(self, reg: Register, value: int):
        self._i2c.writeto_mem(self._addr, CMD_BIT | reg, (value & 0xFF).to_bytes(1, 'little'))

    def write16(self, reg: Register, value: int):
        self._i2c.writeto_mem(self._addr, CMD_BIT | reg, (value & 0xFFFF).to_bytes(2, 'little'))

    def write_bits(self, reg: Register, value: int, mask: int):
        old = self.read8(reg)
        old_masked = old & ~mask
        new = old_masked | value & mask

        self.write8(reg, new)

    def read8(self, reg: Register):
        return struct.unpack('<B', self._i2c.readfrom_mem(self._addr, CMD_BIT | reg, 1))[0]

    def read16(self, reg: Register):
        struct.unpack('<H', self._i2c.readfrom_mem(self._addr, CMD_BIT | reg, 2))

    def get_data(self) -> tuple[int, int, int, int]:
        color_bytes = self._i2c.readfrom_mem(self._addr, CMD_BIT | Register.CDATAL, 4 * 2)
        return struct.unpack('<HHHH', color_bytes)

    def set_integration_time(self, it: int):
        self.write8(Register.ATIME, 0xff - it)

    def set_gain(self, gain: int):
        self.write_bits(Register.CONTROL, gain, 0b11)

    def set_wait(self, wait: int):
        self.write8(Register.ATIME, 0xff - wait)

    def set_wait_long(self, flag: bool):
        self.write_bits(Register.CONFIG, int(flag), 0b1)

    def set_interrupt(self, f):
        self.write_bits(Register.ENABLE, AIEN, AIEN)
        self._interrupt_pin.irq(f, Pin.IRQ_RISING)

    def clear_interrupt(self):
        self.write_bits(Register.ENABLE, ~AIEN, AIEN)
        self._interrupt_pin.irq(None)

    def set_interrupt_limits(self, l: int, h: int):
        self.write16(Register.AILTL, l)
        self.write16(Register.AIHTL, h)

    def set_interrupt_persistance(self, pers: int):
        self.write_bits(Register.PERS, pers, 0b111)

    def set_led(self, state: bool):
        if self._led_pin:
            self._led_pin.value(state)
