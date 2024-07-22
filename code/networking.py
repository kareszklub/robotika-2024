from network import hostname, country, WLAN, STA_IF, STAT_CONNECTING, STAT_GOT_IP
from socket import socket
from array import array
from time import sleep
from config import cfg
import struct

def setup_wifi():
    if 'country' in cfg['network']:
        country(cfg['network']['country'])

    hostname(cfg['network']['hostname'])

    wlan = WLAN(STA_IF)
    wlan.active(True)

    ssid = cfg['network']['creds']['ssid']
    passw = cfg['network']['creds']['password']
    wlan.connect(ssid, passw)

    for attempt in range(1, cfg['network']['attempts'] + 1):
        print(f'connecting to \'{ssid}\' ({attempt=})')
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
        got = sock.readinto(view, n)
        view = view[got:]
        n -= got

    return buf

def recv_u16(sock: socket) -> int:
    return struct.unpack('!H', recv_exact(sock, 2))[0]

def recv_str(sock: socket) -> str:
    return recv_exact(sock, recv_u16(sock)).decode('utf-8')

socks: list[socket] = [None, None]
def setup_dbg():
    dbg_sock = socket()
    dbg_sock.connect((cfg['network']['debug_ip'], cfg['network']['debug_port']))

    socks[0] = dbg_sock

def setup_server() -> int:
    server_sock = socket()
    server_sock.connect((cfg['network']['server_ip'], cfg['network']['server_port']))

    socks[1] = server_sock

    robot_id = recv_u16(server_sock)

    return robot_id
