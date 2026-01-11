"""
Creating a simple TCP Client
Notes:
- SOCK_Stream defines that this is going to be a TCP Client
- The data that we send needs to be in bytes thus encoding is used

Assumptions: 
- The first assumption is that our connection will always succeed
- the second is that the server is always expecting us to send data first (as opposed to servers that expect to send data to you first and await your response). 
- Our third assumption is that the server will always send us data back in a timely fashion
"""

import socket

target_host = "0.0.0.0"
target_port = 1234

# Creating a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Creating a connection
client.connect((target_host,target_port))

# Sending some blank Data
client.sendall(b"GET / HTTPS/1.1 \r\n Host: 0.0.0.0 \r\n\r\n")

# Receiving the Data
response = client.recv(4096)

print(response.decode())

client.close()