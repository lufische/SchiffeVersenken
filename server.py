#!/usr/bin/python           # This is server.py file

import socket               # Import socket module
import numpy as np
import matplotlib.pyplot as pp
import string as st

################################################################################
###                        HELPER FUNCTIONS                                  ###
################################################################################
def setShipsRandom(shipMap, pl):
  # Note: The array is given as reference here and not as a copy
  for shipLen in [5, 4, 4, 3, 3, 3, 2, 2, 2, 2]:
    shipsSet = False
    while not(shipsSet):
      valid = False
      retrySteps = 0
      while not(valid) and (retrySteps<100):
        retrySteps += 1
        coord  = np.random.randint(10, size=2)
        orient = np.random.randint( 2, size=1)[0]
        if (coord[orient] + shipLen < 10): 
          valid = True
        selVert = [max(coord[0]-1, 0), min(coord[0]+(orient==0)*(shipLen-1)+2, 10)]
        selHorz = [max(coord[1]-1, 0), min(coord[1]+(orient==1)*(shipLen-1)+2, 10)]
        if shipMap[selVert[0]:selVert[1], selHorz[0]:selHorz[1], pl].any(): 
          valid = False 
      
      if valid:
        shipMap[coord[0]:coord[0]+(orient==0)*(shipLen-1)+1, 
                coord[1]:coord[1]+(orient==1)*(shipLen-1)+1, pl] = 1
        shipsSet = True
        

def checkDestroyed(shipMap, pl, xy):
  selPl = (pl+1)%2
  if   (xy[0] == 9):
    surr = np.array([-1])
  elif (xy[0] == 0):
    surr = np.array([1])
  else:
    surr = np.array([-1, 1])
    
  if ( (shipMap[xy[0] + surr, xy[1], selPl]%2).any() ):
    itVec = [1, 0]
    xOrient = xy[0]
  else:
    itVec = [0, 1]
    xOrient = xy[1]
    
  selSurr  = np.arange(max(-5, -xOrient), min(5, 9-xOrient)+1, 1, dtype='int')
  fixPos = min(5, xOrient)
  surr = shipMap[xy[0] + itVec[0]*selSurr, xy[1] + itVec[1]*selSurr, selPl]
  waterArea  = (surr%2==0).nonzero()[0]
  intactShip = (surr==1).nonzero()[0]
  dest = [False, False]
  shipStartEnd = [-1, -1]
  
  # Check positive half of surrounding
  arrWater = waterArea[waterArea > fixPos]
  arrShip  = intactShip[intactShip > fixPos]
  if   ( len(arrShip)  == 0 ):                          # No intact ship in positive half       --> pos Half destroyed
    dest[0] = True
    shipStartEnd[1] = 9
  elif ( len(arrWater) == 0 ): dest[0] = False                        # No water in vicinity, but intact ship --> Ship touches border and is not destroyed
  elif ( arrWater[0] < arrShip[0] ):                                  # Both classes appear                   --> Compare what comes first
    dest[0] = True

  # Check negative half of surrounding
  arrWater = waterArea[waterArea < fixPos]
  arrShip  = intactShip[intactShip < fixPos]
  if   ( len(arrShip)  == 0 ): dest[1] = True                         # No intact ship in negative half       --> neg Half destroyed
  elif ( len(arrWater) == 0 ): dest[1] = False                        # No water in vicinity, but intact ship --> Ship touches border and is not destroyed
  else:                        dest[1] = arrWater[-1] > arrShip[-1]   # Both classes appear                   --> Compare what comes first

  # If ship is destroyed set bombed area around ship
  # if (dest[0] and dest[1]):

  return (dest[0] and dest[1])
################################################################################


s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                # Reserve a port for your service.
s.bind((host, port))        # Bind to the port

s.listen(2)                 # Now wait for client connection.

conBots = 0
cls  = [0,0]
adds = [0,0]
while conBots < 1:
  cls[conBots], adds[conBots] = s.accept()     # Establish connection with client.
  print 'Got connection from', adds[conBots]
  cls[conBots].send('Thank you for connecting - You are Player {}'.format(conBots+1))
  conBots += 1

cls[0].send("All set up, lets go!")
# cls[1].send("All set up, lets go!")
# At this point we have two participants connected

# Place ships randomly
shipMap = np.zeros((10, 10, 2))
setShipsRandom(shipMap, 0)
setShipsRandom(shipMap, 1)
print("SHIPS SET UP")

pp.matshow(shipMap[:,:,0])
pp.show()
pp.matshow(shipMap[:,:,1])
pp.show()  


# Handle client commands
def parseCommand(buff, cl, pl):
  if   buff[0] == 'B':
    splittedBuff = buff.split(',')
    xy = [int(splittedBuff[1]), int(splittedBuff[2])]
    if (max(xy)>9 or min(xy)<0):
      cl.send("I")
      return 'I'
    else:
      state = shipMap[xy[0], xy[1], (pl+1)%2]%2
      shipMap[xy[0], xy[1], (pl+1)%2] = state+2
      if (state):
        dest  = checkDestroyed(shipMap, pl, xy)
      else:
        dest = 0

      cl.send("R, {}, {}".format(state, dest))
      
      if (dest == 1):
        pp.matshow(shipMap[:,:,(pl+1)%2])
        pp.plot(xy[1], xy[0], 'ko')
        pp.show()
        
      return  'B'
  elif buff[0] == 'M':
    # Parse map request
    return  'M'
  else:
    # Invalid command
    cl.send("I")
    return 'I'


for steps in range(1000):
  cls[0].send("T")
  for i in range(1000):
    buff = cls[0].recv(1024)
    act = parseCommand(buff, cls[0], 0)
    if (act == 'B'): break
  if ( min(shipMap[shipMap[:,:,1]%2>0,1]) == 3 ):
    break
  
cls[0].send("EOG")
# cls[1].send("EOG")

cls[0].close()                # Close the connection
# cls[1].close()                # Close the connection
