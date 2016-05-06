#!/usr/bin/python           # This is server.py file

import socket               # Import socket module
import numpy as np
import matplotlib.pyplot as pp

################################################################################
###                        HELPER FUNCTIONS                                  ###
################################################################################
def setShipsRandom(shipMap, pl):
  # Note: The array is given as reference here
  for shipLen in [5, 4, 4, 3, 3, 3, 2, 2, 2, 2]:
    shipsSet = False
    while not(shipsSet):
      valid = False
      retrySteps = 0
      while not(valid) and (retrySteps<1000):
        retrySteps += 1
        coord  = np.random.randint(10, size=2)
        orient = np.random.randint( 2, size=1)
        if (coord[orient] + shipLen < 10): 
          valid = True
        selVert = [max(coord[0]-1, 0), min(coord[0]+(orient==0)*(shipLen-1)+2, 10)]
        selHorz = [max(coord[1]-1, 0), min(coord[1]+(orient==1)*(shipLen-1)+2, 10)]
        if shipMap[selVert[0]:selVert[1], selHorz[0]:selHorz[1], pl-1].any(): 
          valid = False 
      
      if valid:
        shipMap[coord[0]:coord[0]+(orient==0)*(shipLen-1)+1, 
                coord[1]:coord[1]+(orient==1)*(shipLen-1)+1, pl-1] = 1
        shipsSet = True
################################################################################


s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                # Reserve a port for your service.
s.bind((host, port))        # Bind to the port

s.listen(2)                 # Now wait for client connection.

conBots = 0
cls  = [0,0]
adds = [0,0]
while conBots < 2:
  cls[conBots], adds[conBots] = s.accept()     # Establish connection with client.
  print 'Got connection from', adds[conBots]
  cls[conBots].send('Thank you for connecting - You are Player {}'.format(conBots+1))
  conBots += 1

cls[0].send("All set up, lets go!")
cls[1].send("All set up, lets go!")
# At this point we have two participants connected

# Place ships randomly
shipMap = np.zeros((10, 10, 2))
setShipsRandom(shipMap, 1)
setShipsRandom(shipMap, 2)
print("SHIPS SET UP")

pp.matshow(shipMap[:,:,0])
pp.show()
pp.matshow(shipMap[:,:,1])
pp.show()  


for steps in range(1000):
  cls[steps%2].send("It is your turn Player {}".format(steps%2))
  buff = cls[steps%2].recv(1024)
  print(buff)

cls[0].close()                # Close the connection
cls[1].close()                # Close the connection
