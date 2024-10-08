from network import hostname, country, WLAN, STA_IF, STAT_CONNECTING
from socket import socket, AF_INET, SOCK_STREAM
from time import sleep_ms
from errno import EAGAIN
from config import cfg
import struct

def setup_wifi():
    if 'country' in cfg['network']:
        country(cfg['network']['country'])

    hostname(cfg['network']['hostname'])

    wlan = WLAN(STA_IF)

    if not wlan.active():
        wlan.active(True)

    if wlan.isconnected():
        return

    ssid = cfg['network']['creds']['ssid']
    passw = cfg['network']['creds']['password']

    wlan.connect(ssid, passw)

    for attempt in range(1, cfg['network']['attempts'] + 1):
        if wlan.status() < 0 or wlan.status() >= 3:
            break

        sleep_ms(100)

    if wlan.isconnected():
        ip = wlan.ifconfig()[0]
    else:
        raise RuntimeError(f'network connection failed ({wlan.status()=})')

def recv_exact(sock: socket, n: int, block=True) -> bytearray | None:
    buf = bytearray(n)
    view = memoryview(buf)

    if not block:
        sock.setblocking(False)

        try:
            b = sock.recv(n)
        except OSError as err:
            if err.errno == EAGAIN:
                return None
            else:
                raise err
        finally:
            sock.setblocking(True)

        view[:len(b)] = b
        n -= len(b)

    while n > 0:
        got = sock.readinto(view, n)
        view = view[got:]
        n -= got

    return buf

def recv_u16(sock: socket, block=True) -> int | None:
    b = recv_exact(sock, 2, block)
    if b is None:
        return None
    else:
        return struct.unpack('!H', b)[0]

def recv_str(sock: socket, block=True) -> str | None:
    l = recv_u16(sock, block)
    if l is None:
        return None
    else:
        return recv_exact(sock, l).decode('utf-8')

socks: list[socket] = [None, None]
def setup_dbg():
    dbg_sock = socket(AF_INET, SOCK_STREAM)
    dbg_sock.connect((cfg['network']['debug_ip'], cfg['network']['debug_port']))

    socks[0] = dbg_sock

def setup_server() -> int:
    server_sock = socket(AF_INET, SOCK_STREAM)
    server_sock.connect((cfg['network']['server_ip'], cfg['network']['server_port']))

    socks[1] = server_sock

    robot_id = recv_u16(server_sock)

    return robot_id
