#!/usr/bin/env python3

import socket, struct

HOST = "127.0.0.1"
PORT = 9999

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s

dbg_sock = connect()
conn = True

controls = {
    'a': True,
    'b': {
        'val': 0,
        'min': -10,
        'max': 10
    },
    'c': 'd',
    'd': {
        'val': 0.0,
        'min': -10.0,
        'max': 10.0
    },
}

def define_controls(ctrls: dict):
    dbg_sock.sendall(b'\02' + struct.pack('!H', len(ctrls)))
    for n in ctrls:
        nb = str(n).encode('utf-8')

        val = ctrls[n]
        ty = -1

        if type(val) is bool:
            ty = b'\00'
            val = struct.pack('!?', val)
        elif type(val) is str:
            ty = b'\03'
            val = str(val).encode('utf-8')
            val = struct.pack('!H', len(val)) + val
        else:
            mn = val['min']
            mx = val['max']
            val = val['val']

            if type(val) is float:
                ty = b'\01'
                val = struct.pack('!3f', val, mn, mx)
            elif type(val) is int:
                ty = b'\02'
                val = struct.pack('!3q', val, mn, mx)

        dbg_sock.sendall(struct.pack('!H', len(nb)) + nb + ty + val)

def dprint(x):
    print(x)

    bs = str(x).encode('utf-8')
    l = struct.pack('!H', len(bs))

    dbg_sock.sendall(b'\01' + l + bs)


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
    print(nm)

    val = ctrls[nm]
    if type(val) is bool:
        val = struct.unpack('!?', recv_exact(1))[0]
    elif type(val) is str:
        l = struct.unpack('!H', recv_exact(2))[0]
        val = recv_exact(l).decode('utf-8')
    else:
        if type(val['val']) is float:
            val['val'] = struct.unpack('!f', recv_exact(4))
        elif type(val['val']) is int:
            val['val'] = struct.unpack('!q', recv_exact(8))

    ctrls[nm] = val


define_controls(controls)
while True:
    recv_change(controls)
    print(controls)
