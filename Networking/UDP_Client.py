"""
Creating a simple UDP Client
Pointers:
- UDP is a connectionless protocol
- Thus, there is no need to establish a connection before sending data
- SOCK_DGRAM defines that this is going to be a UDP Client
- The data that we send needs to be in bytes thus encoding is used
- We receive data along with the address of the sender
"""

import socket

target_host = "127.0.0.1"
target_port = 9999

# Creating a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Sending some data
client.sendto(b"ABBCCCDDDD", (target_host, target_port))

# Receiving some data
data, addr = client.recvfrom(4096)

print(data.decode())

client.close()