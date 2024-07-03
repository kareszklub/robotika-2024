from network import hostname, country, WLAN, STA_IF, STAT_CONNECTING, STAT_GOT_IP
from socket import socket
from time import sleep
from config import cfg
import struct

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

dbg_sock = socket()
dbg_sock.connect((cfg['network']['debug_ip'], cfg['network']['debug_port']))

server_sock = socket()
server_sock.connect((cfg['network']['server_ip'], cfg['network']['server_port']))

recv_buffer = bytearray()
def recv_exact(sock: socket, buffer: bytearray, n: int):
	while n > 0:
		n -= socket.recv_into(buffer, n)

recv_exact(server_sock, recv_buffer, 1)
robot_id = struct.unpack('!H', recv_buffer)
recv_buffer.clear()
