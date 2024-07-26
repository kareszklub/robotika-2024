from networking import recv_exact, recv_str, socks
from math import floor
import struct

def define_controls(ctrls: dict):
    sock = socks[0]

    sock.sendall(struct.pack('!BH', 2, len(ctrls)))

    for n in ctrls:
        nb = str(n).encode('utf-8')

        ctrl = ctrls[n]
        val = ctrl._val

        ty = None
        res = None

        if ctrl.val_is_instance(bool):
            ty = b'\x00'
            res = struct.pack('!?', val)
        elif ctrl.val_is_instance(float):
            ty = b'\x01'
            res = struct.pack('!3f', val, ctrl._min, ctrl._max)
        elif ctrl.val_is_instance(int):
            ty = b'\x02'
            res = struct.pack('!3q', val, ctrl._min, ctrl._max)
        elif ctrl.val_is_instance(str):
            ty = b'\x03'
            res = val.encode('utf-8')
            res = struct.pack('!H', len(res)) + res
        elif ctrl.val_is_instance(tuple):
            ty = b'\x04'
            res = struct.pack(
                '!3B',
                floor(ctrl[0] * 255),
                floor(ctrl[1] * 255),
                floor(ctrl[2] * 255)
            )

        sock.sendall(struct.pack('!H', len(nb)) + nb + ty + res)

def dprint(x):
    print(x)

    bs = str(x).encode('utf-8')
    l = struct.pack('!BH', 1, len(bs))

    socks[0].sendall(l + bs)

def recv_change(ctrls: dict):
    sock = socks[0]

    nm = recv_str(sock, False)
    if nm is None:
        return

    ctrl = ctrls[nm]
    if ctrl.val_is_instance(bool):
        val = struct.unpack('!?', recv_exact(sock, 1))[0]
    elif ctrl.val_is_instance(float):
        val = struct.unpack('!f', recv_exact(sock, 4))[0]
    elif ctrl.val_is_instance(int):
        val = struct.unpack('!q', recv_exact(sock, 8))[0]
    elif ctrl.val_is_instance(str):
        val = recv_str(sock)
    elif ctrl.val_is_instance(tuple):
        val = struct.unpack('!3B', recv_exact(sock, 3))
        val = (
            val[0] / 255,
            val[1] / 255,
            val[2] / 255,
        )

    ctrl.update(val)
