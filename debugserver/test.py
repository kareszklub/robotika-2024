#!/usr/bin/env python3

import socket, struct

HOST = "127.0.0.1"
PORT = 9999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def send(_msg: str):
    msg = _msg.encode("utf-8")
    s.sendall(b"\x01")
    s.sendall(struct.pack("!H", len(msg)))
    s.sendall(msg)


send("buffher?")
send("i barely know her")

s.close()
