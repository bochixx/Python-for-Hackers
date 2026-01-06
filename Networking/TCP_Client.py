"""
Creating a simple TCP Client
Pointers:
- SOCK_Stream defines that this is going to be a TCP Client
- The data that we send needs to be in bytes thus encoding is used
"""

import socket

target_host = "www.example.com"
target_port = 80

# Creating a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Creating a connection
client.connect((target_host,target_port))

# Sending some blank Data
client.sendall(b"GET / HTTPS/1.1 \r\n Host: example.com \r\n\r\n")

# Receiving the Data
response = client.recv(4096)

print(response.decode())