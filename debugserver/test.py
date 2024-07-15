#!/usr/bin/env python3

import socket, struct, time

HOST = "127.0.0.1"
PORT = 9999

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s

def send(s: socket.socket, _msg: str):
    print(_msg)
    msg = _msg.encode("utf-8")
    s.sendall(b"\x01")
    s.sendall(struct.pack("!H", len(msg)))
    s.sendall(msg)

s = connect()
conn = True

# send("buffher?")
# send("i barely know her")

while True:
    try:

        i = 0
        while True:
            send(s, f"bruh moment numero {i}")
            i += 1
            time.sleep(1)

    except socket.error:
        conn = False
        print("[disconnected]")
        while not conn:
            try:
                s = connect()
                conn = True
                print("[reconnected]")
            except socket.error:
                print("[reconnect failed]")
                time.sleep(1)
