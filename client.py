#!/usr/bin/python           # This is client.py file

import socket               # Import socket module
import numpy as np

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                # Reserve a port for your service.

s.connect((host, port))
print s.recv(1024)          # Handshake positive

while True:
  buff = s.recv(1024)        # Start Turn
  if (buff == 'T'):
    s.send("B, {}, {}".format(np.random.randint(10), np.random.randint(10)))
    buff = s.recv(1024)        # Result
    print(buff)
  if (buff == "EOG"): break
  

s.close                     # Close the socket when done
