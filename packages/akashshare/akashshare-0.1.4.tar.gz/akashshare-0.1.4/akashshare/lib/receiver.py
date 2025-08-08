import socket
from tqdm import tqdm  # Add this to your requirements.txt

def start_tcp_receiver(server_ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((server_ip, port))

    # Read filename
    filename_bytes = b""
    while not filename_bytes.endswith(b'\n'):
        filename_bytes += s.recv(1)
    filename = filename_bytes.strip().decode()

    # Read filesize
    filesize_bytes = b""
    while not filesize_bytes.endswith(b'\n'):
        filesize_bytes += s.recv(1)
    filesize = int(filesize_bytes.strip().decode())

    with open(filename, 'wb') as f, tqdm(total=filesize, unit='B', unit_scale=True, desc=filename) as pbar:
        while True:
            data = s.recv(1024)
            if not data:
                break
            f.write(data)
            pbar.update(len(data))

    print(f"[TCP] File received and saved as '{filename}'")
    s.close()
