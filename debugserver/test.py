#!/usr/bin/env python3

from socket import socket
from math import floor
import struct

HOST = "127.0.0.1"
PORT = 9999

dbg_sock = socket()
dbg_sock.connect((HOST, PORT))

def define_controls(ctrls: dict):
    dbg_sock.sendall(b'\02' + struct.pack('!H', len(ctrls)))

    for n in ctrls:
        nb = str(n).encode('utf-8')

        val = ctrls[n]
        ty = -1

        if isinstance(val, bool):
            ty = b'\00'
            val = struct.pack('!?', val)
        elif isinstance(val, str):
            ty = b'\03'
            val = str(val).encode('utf-8')
            val = struct.pack('!H', len(val)) + val
        elif isinstance(val, dict):
            mn = val['min']
            mx = val['max']
            val = val['val']

            if isinstance(val, float):
                ty = b'\01'
                val = struct.pack('!3f', val, mn, mx)
            elif isinstance(val, int):
                ty = b'\02'
                val = struct.pack('!3q', val, mn, mx)

        elif isinstance(val, tuple):
            ty = b'\04'
            val = struct.pack('!3B', floor(val[0] * 255), floor(val[1] * 255), floor(val[2] * 255))

        dbg_sock.sendall(struct.pack('!H', len(nb)) + nb + ty + val)

def dprint(x):
    print(x)

    bs = str(x).encode('utf-8')
    l = struct.pack('!cH', b'\01', len(bs))

    dbg_sock.sendall(l + bs)

def recv_exact(n: int) -> bytearray:
    buf = bytearray(n)
    view = memoryview(buf)

    while n:
        nbytes = dbg_sock.recv_into(view, n)
        view = view[nbytes:]
        n -= nbytes

    return buf

def recv_change(ctrls: dict):
    nl = struct.unpack('!H', recv_exact(2))[0]
    nm = recv_exact(nl).decode('utf-8')

    val = ctrls[nm]
    if isinstance(val, bool):
        val = struct.unpack('!?', recv_exact(1))[0]
    elif isinstance(val, str):
        l = struct.unpack('!H', recv_exact(2))[0]
        val = recv_exact(l).decode('utf-8')
    elif isinstance(val, dict):
        if isinstance(val['val'], float):
            val['val'] = struct.unpack('!f', recv_exact(4))[0]
        elif isinstance(val['val'], int):
            val['val'] = struct.unpack('!q', recv_exact(8))[0]
    elif isinstance(val, tuple):
        val = struct.unpack('!3B', recv_exact(3))
        val = (
            val[0] / 255,
            val[1] / 255,
            val[2] / 255,
        )

    ctrls[nm] = val

controls = {
    'checky': True,

    'inty': {
        'val': 0,
        'min': -100,
        'max': 100
    },

    'stringy': 'lorem ipsum',

    'floaty': {
        'val': 0.0,
        'min': -10.0,
        'max': 10.0
    },

    'colory': (1.0, 0.0, 0.0),
}

for i in range(3):
    dprint('pluh' + i * ' pluh')

define_controls(controls)

try:
    while True:
        recv_change(controls)
        dprint(controls)
except KeyboardInterrupt:
    pass
