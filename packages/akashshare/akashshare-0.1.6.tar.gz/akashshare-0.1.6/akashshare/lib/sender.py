import socket
import os
import time

def send_file(file_path, client_ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', port))
    s.listen(1)
    print(f"[TCP] Waiting for receiver on port {port}...")

    # Add small delay to ensure the socket is ready before accepting
    time.sleep(1)

    conn, addr = s.accept()
    print(f"[TCP] Connected to {addr}")

    filename = os.path.basename(file_path)
    filesize = os.path.getsize(file_path)

    # Send filename and filesize, separated by newline
    conn.send(f"{filename}\n{filesize}\n".encode())

    with open(file_path, 'rb') as f:
        while chunk := f.read(1024):
            conn.send(chunk)

    print(f"[TCP] Sent file '{filename}' ({filesize} bytes)")
    conn.close()
    s.close()
