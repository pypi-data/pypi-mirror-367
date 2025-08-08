# src/lib/sender.py
import socket
import os

def send_file(file_path, client_ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))
    s.listen(1)
    print(f"[TCP] Waiting for receiver on port {port}")
    conn, addr = s.accept()
    print(f"[TCP] Connected to {addr}")

    with open(file_path, 'rb') as f:
        while chunk := f.read(1024):
            conn.send(chunk)

    print(f"[TCP] Sent file {os.path.basename(file_path)}")
    conn.close()
    s.close()
