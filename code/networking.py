from network import hostname, country, WLAN, STA_IF, STAT_CONNECTING, STAT_GOT_IP
from socket import socket
from time import sleep
from config import cfg
import struct

def setup_wifi():
    if 'country' in cfg['network']:
        country(cfg['network']['country'])

    hostname(cfg['network']['hostname'])

    wlan = WLAN(STA_IF)
    wlan.active(True)

    wlan.connect(cfg['network']['ssid'], cfg['network']['password'])

    for attempt in range(1, cfg['network']['attempts'] + 1):
        print(f'connecting to wifi ({attempt=})')
        if wlan.status() != STAT_CONNECTING:
            break
        sleep(1)

    if wlan.status() == STAT_GOT_IP:
        ip = wlan.ifconfig()[0]
        print(f'connected, {ip=}')
    else:
        raise RuntimeError(f'network connection failed ({wlan.status()=})')

def recv_exact(sock: socket, n: int) -> bytearray:
    buf = bytearray(n)
    view = memoryview(buf)

    while n > 0:
        got = sock.recv_into(view, n)
        view = view[got:]
        n -= got

    return buf

def recv_u16(sock: socket) -> int:
    return struct.unpack('!H', recv_exact(sock, 2))[0]

def recv_str(sock: socket) -> str:
    return recv_exact(sock, recv_u16(sock)).decode('utf-8')

def setup_dbg() -> socket:
    dbg_sock = socket()
    dbg_sock.connect((cfg['network']['debug_ip'], cfg['network']['debug_port']))
    return dbg_sock

def setup_server() -> tuple[socket, int]:
    server_sock = socket()
    server_sock.connect((cfg['network']['server_ip'], cfg['network']['server_port']))

    robot_id = recv_u16(server_sock)

    return robot_id
