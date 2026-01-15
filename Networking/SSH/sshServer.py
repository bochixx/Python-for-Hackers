import socket
import paramiko
import threading
import sys
import argparse
from pathlib import Path


# Using the key from the Paramiko demo files
host_key = paramiko.RSAKey(filename='test_rsa.key')

class Server (paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self, username, password):
        if(username == 'user') and (password == 'passwd'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
    
    def check_channel_shell_request(self, channel):
        self.event.set()
        return True
    
    def check_channel_exec_request(self, channel, command):
        self.event.set()
        return True
    
def run_server(host: str, port: int, key_path: Path):
    if not key_path.exists():
        raise FileNotFoundError(f"Host key not found: {key_path}")
    host_key = paramiko.RSAKey(filename=str(key_path))

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(100)
    print(f"[+] Listening on {host}:{port} ...")

    try:
        client, addr = sock.accept()
        print(f"[+] Got a connection from {addr}")
        bhSession = paramiko.Transport(client)
        bhSession.add_server_key(host_key)
        server = Server()
        bhSession.start_server(server=server)

        chan = bhSession.accept(20)
        if chan is None:
            print("[-] No channel...")
            return
        print("[+] Authenticated!")

        # Wait for shell request before proceeding
        server.event.wait(10)

        chan.send(b"Welcome to bh_ssh :)")
        while True:
            cmd = input("Enter Command: ").strip()
            if cmd.lower() == "exit":
                chan.send(b"exit")
                print("Exiting...")
                break
            chan.send(cmd.encode())
            resp = chan.recv(1024)
            if not resp:
                break
            print(resp.decode(errors="replace") + "\n")
    finally:
        try:
            bhSession.close()
        except Exception:
            pass
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Paramiko SSH server")
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    parser.add_argument("--key", default="test_rsa.key", help="Path to RSA host key")
    args = parser.parse_args()
    run_server(args.host, args.port, Path(args.key))