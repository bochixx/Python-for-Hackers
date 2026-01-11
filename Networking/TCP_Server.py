"""
Creating a simple TCP Server
"""

import socket
import threading

bind_ip = "0.0.0.0"
bind_port = 1234

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    # Pass in the IP address and port we want the server to listen on
    server.bind((bind_ip, bind_port))

    # Tell the server to start listening with a maximum backlog of connections set to 3
    server.listen(3)
    print("[*] Listening on %s:%d" % (bind_ip,bind_port))

    def handle_client(client_socket):
        # Print out what the client needs
        req = client_socket.recv(1024).decode()
        print("[*] Received: %s " % req)

        # Send back a packet
        client_socket.send("ACK".encode())

        client_socket.close()

    # Putting the server in its main loop, where it is waiting for an incoming connection
    while True:
        # When a client connects, we receive the client socket into the client variable, and the remote connection details into the addr variable
        client, addr = server.accept()
        print("[*] Accepted connection from %s:%d" % (addr[0], addr[1]))

        # Create a new thread object that points to our handle_client function, and we pass it the client socket object as an argument
        client_handler = threading.Thread(target=handle_client,args=(client,))

        client_handler.start()

except KeyboardInterrupt:
    print("[*] Shutting down server...")

finally:
    server.close()