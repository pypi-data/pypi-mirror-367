import time  # ADD THIS
from InquirerPy import inquirer
from akashshare.lib.discovery import udp_discovery_server, udp_discovery_client
from akashshare.lib.sender import send_file
from akashshare.lib.receiver import start_tcp_receiver
from akashshare.utils.helper import get_filename, get_dirname, get_file_names_from_dir
import os


def handle_send_action():
    choice = inquirer.select(
        message="What do you want to send?",
        choices=["File", "Directory (coming soon)", "Back"],
    ).execute()

    if choice.lower() == "file":
        file_path = input("Enter absolute file path to send: ").strip()

        if not os.path.isfile(file_path):
            print("[!] Invalid file path.")
            return

        print(f"[INFO] Waiting for receiver to discover us via UDP...")

        receiver_ip = udp_discovery_server()

        if receiver_ip:
            time.sleep(1)  # ADD THIS: Give receiver time to connect
            send_file(file_path, receiver_ip, port=50001)
        else:
            print("[UDP] No receiver found.")

    elif choice.lower().startswith("directory"):
        print("[TODO] Directory sharing is coming soon.")

    else:
        return


def handle_receive_action():
    print("[INFO] Looking for a sender (broadcasting UDP)...")

    sender_ip = udp_discovery_client()
    if sender_ip:
        start_tcp_receiver(server_ip=sender_ip, port=50001)
    else:
        print("[UDP] No sender found.")


def handle_exit_action():
    print("Happy Sharing! Bye 👋")
    exit(0)
