import socket
import time
import sys
from tqdm import tqdm  # progress bar

def spinner():
    # Simple spinner animation generator
    while True:
        for cursor in '|/-\\':
            yield cursor

def start_tcp_receiver(server_ip, port, max_attempts=5, delay=1):
    attempt = 1
    spin = spinner()

    while attempt <= max_attempts:
        sys.stdout.write(f"\r[TCP] Attempt {attempt}: Connecting to {server_ip}:{port} {next(spin)} ")
        sys.stdout.flush()

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((server_ip, port))
            sys.stdout.write("\r[TCP] Connected!                      \n")
            sys.stdout.flush()
            break
        except (ConnectionRefusedError, OSError) as e:
            # Instead of printing error directly, just continue spinner & delay
            time.sleep(delay)
            attempt += 1
    else:
        print(f"\n[TCP] Could not connect to sender after {max_attempts} attempts.")
        return

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
