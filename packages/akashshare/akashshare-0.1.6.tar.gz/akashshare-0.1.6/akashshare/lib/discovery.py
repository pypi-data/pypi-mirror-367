# src/lib/discovery.py

import socket
from akashshare.utils import UDP_PORT, DISCOVERY_MSG, RESPONSE_MSG

def udp_discovery_server():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.bind(("", UDP_PORT))
    print(f"UDP Discovery server listening on port {UDP_PORT}")

    while True:
        data, addr = udp.recvfrom(1024)
        if data.decode() == DISCOVERY_MSG:
            print(f"[UDP] Discovery server request from {addr}")
            udp.sendto(RESPONSE_MSG.encode(), addr)
            return addr[0]

def udp_discovery_client():
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp.settimeout(5)

    print("[UDP] Broadcasting for server...")
    udp.sendto(DISCOVERY_MSG.encode(), ('<broadcast>', UDP_PORT))
    try:
        data, addr = udp.recvfrom(1024)
        if data.decode() == RESPONSE_MSG:
            print(f"[UDP] Found server at {addr[0]}")
            return addr[0]
    except socket.timeout:
        print("UDP broadcast timed out.")
    return None
