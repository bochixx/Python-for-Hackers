"""
TCP Proxy
- This script sets up a TCP proxy that listens on a specified local host and port, forwards traffic to a specified remote host and port. 
- It can optionally receive data from the remote host before sending any data from the local host.

Usage:
    Terminal 1 (Remote Host): nc -l -p 6001
    Terminal 2 (Proxy): sudo python3 proxy.py 127.0.0.1 6000 127.0.0.1 6001 False
    Terminal 3 (Local Host): nc 127.0.0.1 6000
"""

import sys
import socket
import threading

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(e)
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions")
        sys.exit(1)     # Non-zero value denotes a failure

    print("[*] Listening on %s:%d" % (local_host, local_port))

    server.listen(3)

    while True:
        client_socket, addr = server.accept()

        # Printing the local connection information
        print("[==>] Received incoming connection from %s:%d" % (addr[0], addr[1]))

        # Starting a thread to talk with the remote host
        proxy_thread = threading.Thread(
            target=proxy_handler, 
            args=(client_socket, remote_host, remote_port, receive_first))
        
        proxy_thread.start()


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # Connect to the remote host
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        remote_socket.connect((remote_host, remote_port))
    except ConnectionRefusedError:
        print(f"[!!] Unable to connect to {remote_host}:{remote_port}")
        client_socket.close()
        return

    # Receive data from the remote end if necessay:
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # Send this to our response handler
        remote_buffer = response_handler(remote_buffer)

        # If wwe have data to send to our local client, send it
        if len(remote_buffer):
            print("[<==] Sending %d bytes to local host" % len(remote_buffer))
            client_socket.send(remote_buffer)
    
    # Now lets loop and read from local
    # Send to remote, send to local
    # Rinse, Wash, Repeat
    while True:
        # Read from local host
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print("[==>] Received %d bytes from local host" % len(local_buffer))
            hexdump(local_buffer)

            # Send it to our request handler
            local_buffer = request_handler(local_buffer)

            # Send off the data to the remote host
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote...")

        # Receive back the response
        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print("[<==] Received %d bytes from remote" % len(remote_buffer))
            hexdump(remote_buffer)

            # Send it to our response handler
            remote_buffer = response_handler(remote_buffer)

            # Send off the data to the local socket
            client_socket.send(remote_buffer)
            print("[<==] Sent to local host...")

        # If no more data on either side, close the connection
        if not local_buffer and not remote_buffer:
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            sys.exit(0)
            break


def hexdump(src, length=16):
    # this is a pretty hex dumping function directly taken from the comments here 
    # and modified for compatibility for Python3:
    # http://code.activestate.com/recipes/142812-hex-dumper/
    result = []
    for i in range(0, len(src), length):
        chunk = src[i:i + length]
        hexa = ' '.join(f'{b:02X}' for b in chunk)
        text = ''.join(chr(b) if 0x20 <= b < 0x7F else '.' for b in chunk)
        result.append(f'{i:04X}   {hexa:<{length * 3}}   {text}')
    print('\n'.join(result))


def receive_from(connection):
    buffer = b""

    # Set a 10 sec timeout depending on the target this may be need to be adjusted
    connection.settimeout(10)

    try:
        # Keep reading into the buffer until no more data
        # or we timeout
        while True:
            data = connection.recv(4096)

            if not data:
                break

            buffer += data
    
    except socket.timeout:
        pass

    return buffer


# Modify any responses destined for the local host
def response_handler(buffer):
    # Some code to perform packet modifications
    return buffer 


# Modify any requests destined for the remote host
def request_handler(buffer):
    # Some code to perform packet modifications
    return buffer


def main():
    # Check if required args are not passed
    if len(sys.argv[1:]) != 5:
        print("Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 6000 10.11.123.1 6000 True")
        sys.exit(0)

    # setup local listening parameters
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    # setup remote target
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    # This tells our proxy to connect and receive data before sending to remote host
    receive_first = sys.argv[5]

    if receive_first.lower() == "true":
        receive_first = True
    else:
        receive_first = False
    
    # Now spinning up our listening port
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)


if __name__ == "__main__":
    main()