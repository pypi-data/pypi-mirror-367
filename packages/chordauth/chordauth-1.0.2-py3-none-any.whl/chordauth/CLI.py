import pinggy
from threading import Thread
import time
import socket
import pyperclip
import argparse
def wait_for_server(host, port, timeout=120):
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            if time.time() - start_time > timeout:
                return False
            time.sleep(0.5)
def start_flask():
    from chordauth.FlaskApp import run_app
    run_app()
    
def start_dashboard_thread():
    from chordauth.AdminDashboard import start_dashboard
    start_dashboard()

def main():
    parser = argparse.ArgumentParser(description="ChordAuth")
    subparsers = parser.add_subparsers(dest="command")
    server_parser = subparsers.add_parser("server", help="Start ChordAuth auth server.")
    dashboard_parser = subparsers.add_parser("dashboard", help="Start ChordAuth admin dashboard.")
    info_parser = subparsers.add_parser("info", help="Get info about ChordAuth.")

    args = parser.parse_args()
    if args.command is None:
        args.command = "info"
    if args.command == "server":
        flask_thread = Thread(target=start_flask)
        flask_thread.start()
        if wait_for_server("127.0.0.1", 5001):
            tunnel = pinggy.start_tunnel(forwardto="127.0.0.1:5001")
            print(f"Server started. Link is available at {tunnel.urls[1]}")
            
            pyperclip.copy(tunnel.urls[1])
            print("Link copied to clipboard.")
            print("To close ChordAuth, close the terminal window or force quit it.")
            print("Thank you for using ChordAuth 🎹🔑😃")
        else:
            print("Server timed out.")

    elif args.command == "dashboard":
        start_dashboard_thread()
    elif args.command == "info":
        print("ℂ𝕙𝕠𝕣𝕕𝔸𝕦𝕥𝕙")
        print("by SeafoodStudios")
        print("ChordAuth is a decentralized authentication system.")
        print("Learn more at 'https://github.com/SeafoodStudios/ChordAuth'!")
        print("Thank you!")
        print("😃")
    else:
        print("Invalid command.")

if __name__ == "__main__":
    main()
