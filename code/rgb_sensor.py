from machine import I2C, Pin
from time import sleep_ms
import struct

DEFAULT_ADDRESS = const(0x29)
CMD_BIT = const(0x80)

class Register:
    ENABLE  = const(0x00)
    ATIME   = const(0x01)
    WTIME   = const(0x03)
    AILTL   = const(0x04)
    AILTH   = const(0x05)
    AIHTL   = const(0x06)
    AIHTH   = const(0x07)
    PERS    = const(0x0C)
    CONFIG  = const(0x0D)
    CONTROL = const(0x0F)
    ID      = const(0x12)
    STATUS  = const(0x13)
    CDATAL  = const(0x14)
    CDATAH  = const(0x15)
    RDATAL  = const(0x16)
    RDATAH  = const(0x17)
    GDATAL  = const(0x18)
    GDATAH  = const(0x19)
    BDATAL  = const(0x1A)
    BDATAH  = const(0x1B)

PON  = const(0x01)
AEN  = const(0x02)
WEN  = const(0x08)
AIEN = const(0x10)

class RgbSensor:
    _addr: int
    _i2c: I2C

    _interrupt_pin: Pin | None
    _led_pin: Pin | None

    def __init__(
            self, i2c: I2C, addr: int = DEFAULT_ADDRESS,
            led_pin: Pin | None = None, interrupt_pin: Pin | None = None,
            integration_time: int = 0, gain: int = 0
        ):
        self._interrupt_pin = interrupt_pin
        self._led_pin = led_pin
        self._addr = addr
        self._i2c = i2c

        self._write_bits(Register.ENABLE, PON, PON)
        sleep_ms(10)
        self._write_bits(Register.ENABLE, AEN, AEN)

        if integration_time:
            self.set_integration_time(integration_time)
        if gain:
            self.set_gain(gain)

    def _write8(self, reg: int, value: int):
        self._i2c.writeto_mem(self._addr, CMD_BIT | reg, (value & 0xFF).to_bytes(1, 'little'))

    def _write16(self, reg: int, value: int):
        self._i2c.writeto_mem(self._addr, CMD_BIT | reg, (value & 0xFFFF).to_bytes(2, 'little'))

    def _write_bits(self, reg: int, value: int, mask: int):
        old = self._read8(reg)
        old_masked = old & ~mask
        new = old_masked | value & mask

        self._write8(reg, new)

    def _read8(self, reg: int) -> int:
        return struct.unpack('<B', self._i2c.readfrom_mem(self._addr, CMD_BIT | reg, 1))[0]

    def _read16(self, reg: int) -> int:
        return struct.unpack('<H', self._i2c.readfrom_mem(self._addr, CMD_BIT | reg, 2))[0]

    def get_data(self) -> tuple[int, int, int, int]:
        color_bytes = self._i2c.readfrom_mem(self._addr, CMD_BIT | Register.CDATAL, 4 * 2)
        return struct.unpack('<HHHH', color_bytes)

    def set_integration_time(self, it: int):
        self._write8(Register.ATIME, 0xff - it)

    def set_gain(self, gain: int):
        self._write_bits(Register.CONTROL, gain, 0b11)

    def set_wait(self, wait: int):
        self._write8(Register.ATIME, 0xff - wait)

    def set_wait_long(self, flag: bool):
        self._write_bits(Register.CONFIG, int(flag), 0b1)

    def set_interrupt(self, f):
        self._write_bits(Register.ENABLE, AIEN, AIEN)
        if self._interrupt_pin:
            self._interrupt_pin.irq(f, Pin.IRQ_RISING)

    def clear_interrupt(self):
        self._write_bits(Register.ENABLE, ~AIEN, AIEN)
        if self._interrupt_pin:
            self._interrupt_pin.irq(None)

    def set_interrupt_limits(self, l: int, h: int):
        self._write16(Register.AILTL, l)
        self._write16(Register.AIHTL, h)

    def set_interrupt_persistance(self, pers: int):
        self._write_bits(Register.PERS, pers, 0b111)

    def set_led(self, state: bool):
        if self._led_pin:
            self._led_pin.value(state)
