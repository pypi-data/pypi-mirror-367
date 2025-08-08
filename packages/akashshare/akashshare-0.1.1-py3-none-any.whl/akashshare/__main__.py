# src/main.py
from InquirerPy import inquirer
from akashshare.lib import handle_send_action, handle_receive_action, handle_exit_action

if __name__ == "__main__":
    while True:
        choice = inquirer.select(
            message="Choose an action",
            choices=["Send", "Receive", "Exit"],
        ).execute()
        
        if choice == "Send":
            handle_send_action()
        elif choice == "Receive":
            handle_receive_action()
        else:
            handle_exit_action()
