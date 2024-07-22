from networking import recv_exact, recv_str, socks
import struct

def define_controls(ctrls: dict):
    sock = socks[0]

    sock.sendall(b'\02' + struct.pack('!H', len(ctrls)))

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

        sock.sendall(struct.pack('!H', len(nb)) + nb + ty + val)

def dprint(x):
    print(x)

    bs = str(x).encode('utf-8')
    l = struct.pack('!H', len(bs))

    socks[0].sendall(b'\01' + l + bs)

def recv_change(ctrls: dict):
    sock = socks[0]

    nm = recv_str(sock)

    ty = type(ctrls[nm])
    if ty is bool:
        ctrls[nm] = struct.unpack('!?', recv_exact(sock, 1))[0]
    elif ty is str:
        ctrls[nm] = recv_str(sock)
    else:
        ty = type(ctrls[nm]['val'])
        if ty is float:
            ctrls[nm]['val'] = struct.unpack('!f', recv_exact(sock, 4))[0]
        elif ty is int:
            ctrls[nm]['val'] = struct.unpack('!q', recv_exact(sock, 8))[0]
