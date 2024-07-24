from networking import recv_exact, recv_str, socks
import struct

def define_controls(ctrls: dict):
    sock = socks[0]

    sock.sendall(struct.pack('!BH', 2, len(ctrls)))

    # TODO: check DbgNum._val for type
    for n in ctrls:
        nb = str(n).encode('utf-8')

        val = ctrls[n]
        ty = -1

        if isinstance(val, bool):
            ty = b'\x00'
            val = struct.pack('!?', val)
        elif isinstance(val, str):
            ty = b'\x03'
            val = str(val).encode('utf-8')
            val = struct.pack('!H', len(val)) + val
        elif isinstance(val, dict):
            mn = val['min']
            mx = val['max']
            val = val['val']

            if isinstance(val, float):
                ty = b'\x01'
                val = struct.pack('!3f', val, mn, mx)
            elif isinstance(val, int):
                ty = b'\x02'
                val = struct.pack('!3q', val, mn, mx)

        elif isinstance(val, tuple):
            ty = b'\x04'
            val = struct.pack('!3B', floor(val[0] * 255), floor(val[1] * 255), floor(val[2] * 255))

        sock.sendall(struct.pack('!H', len(nb)) + nb + ty + val)

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

    ctrls[nm].update(val)
