# src/lib/receiver.py
import socket

def start_tcp_receiver(server_ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, port))

    with open("received_file", 'wb') as f:
        while True:
            data = s.recv(1024)
            if not data:
                break
            f.write(data)

    print("[TCP] File received.")
    s.close()
