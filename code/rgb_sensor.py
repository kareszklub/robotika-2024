# from enum import IntEnum
IntEnum = int

from machine import I2C
from time import sleep
import struct

DEFAULT_ADDRESS = 0x29
CMD_BIT = 0x80

class Register(IntEnum):
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

class EnableRegisterField(IntEnum):
    PON  = 0x01
    AEN  = 0x02
    WEN  = 0x08
    AIEN = 0x10

class RgbSensor:
    _addr: int
    _i2c: I2C

    def __init__(self, i2c: I2C, addr = DEFAULT_ADDRESS):
        self._i2c = i2c
        self._addr = addr

        self.write_bits(Register.ENABLE, 1, EnableRegisterField.PON)
        sleep(0.003)
        self.write_bits(Register.ENABLE, 1, EnableRegisterField.AEN)

    def write8(self, reg: Register, value: int):
        self._i2c.writeto_mem(self._addr, CMD_BIT | reg, (value & 0xFF).to_bytes())

    def write16(self, reg: Register, value: int):
        self._i2c.writeto_mem(self._addr, CMD_BIT | reg, (value & 0xFFFF).to_bytes(2))

    def write_bits(self, reg: Register, value: int, mask: int):
        old = self.read8(reg)
        old_masked = old & ~mask
        new = old_masked | value & mask

        self.write8(reg, new)

    def read8(self, reg: Register):
        return struct.unpack('<B', self._i2c.readfrom_mem(self._addr, CMD_BIT | reg, 1))

    def read16(self, reg: Register):
        struct.unpack('<H', self._i2c.readfrom_mem(self._addr, CMD_BIT | reg, 2))

    def getData(self) -> tuple[int, int, int, int]:
        color_bytes = self._i2c.readfrom_mem(self._addr, CMD_BIT | Register.CDATAL, 4 * 2)
        return struct.unpack('<HHHH', color_bytes)

    def setIntegrationTime(self, it: int):
        self.write8(Register.ATIME, 0xff - it)

    def setGain(self, gain: int):
        self.write_bits(Register.CONTROL, gain, 0b11)

    def setWait(self, wait: int):
        self.write8(Register.ATIME, 0xff - wait)

    def setWaitLong(self, flag: bool):
        self.write_bits(Register.CONFIG, int(flag), 0b1)

    def setInterrupt(self, flag: bool):
        self.write_bits(Register.ENABLE, int(flag), EnableRegisterField.AIEN)

    def setIntLimits(self, l: int, h: int):
        self.write16(Register.AILTL, l)
        self.write16(Register.AIHTL, h)

    def setInterruptPersistance(self, pers: int):
        self.write_bits(Register.PERS, pers, 0b111)

def calculateColorTemperature(self, r: int, g: int, b: int) -> int:
    pass

def calculateColorTemperature_dn40(self, r: int, g: int, b: int, c: int) -> int:
    pass

def calculateLux(self, r: int, g: int, b: int) -> int:
    pass
