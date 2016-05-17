#!/usr/bin/python           # This is server.py file

import socket               # Import socket module
import numpy as np
import matplotlib.pyplot as pp
import string as st
import time

debug = True
visu  = False


################################################################################
###                        HELPER FUNCTIONS                                  ###
################################################################################
def saveSend(sock, command):
  """Sends the command to the server and checks if the command
  was submitted correctly
  Inout:
    command:     string
  Return:
    int          successfull. Raises error if not."""
  sent = sock.send(command)
  for i in range(10):
    if (sent < len(command)) and debug:
      print('ERROR> During sending - Retry')
    else:
      time.sleep(0.0005)
      return 1
  if (sent == 0):
    raise "ERROR> No communication with server possible"
    return 0
    




def setShipsRandom(shipMap):
  """Place ships randomly on the map. The implemented rule ensures, that ships
  can be placed on the border, but are not allowed to touch (neither
  directly nor diagonally).
  All in all this function places
    1 Aircraft carrier (length 5)
    2 Battleships (length 4)
    3 Destroyer (lenght 3)
    4 Submarines (lenght 2)
  Input: 
    shipMap:    numpy.array (as reference, standard) specifying the ship
                positions.
    pl:         Player index
  """
  # Note: The shipMap array is given as reference here and not as a copy
  #       Dependend on the position of the larger ships, it is possible
  #       that no space for the smaller ships is left. Therefore we just
  #       start all over again if such a case occurs.
  # Developper Note: @MU suggested, that it is more efficient to call the
  #                  ship placement recursively.
  
  # ================================ INIT ======================================
  maxResetTries   = 1000 # Max Number of attempts for whole configuration
  maxShipSetSteps = 1000 # Max Number of tries to set ship
  
  # ============================== SET SHIPS ===================================
  resetSteps = 0
  shipsSet = False # Flag: Are all ships correctly set?
  while not(shipsSet) and (resetSteps<1000):
    # Start settin the ships from large to small
    for shipLen in [5, 4, 4, 3, 3, 3, 2, 2, 2, 2]:
      valid    = False # Flag: Is the current position for one ship valid?
      retrySteps = 0
      # Randomly draw position and orientation for current ship until it
      # is valid
      while not(valid) and (retrySteps<1000):
        retrySteps += 1
        coord  = np.random.randint(10, size=2)
        orient = np.random.randint( 2, size=1)[0]
        # Check if ship fits in the game field
        if (coord[orient] + shipLen < 10): 
          valid = True
        # Check if ship touches other ship
        selVert = [max(coord[0]-1, 0), min(coord[0]+(orient==0)*(shipLen-1)+2, 10)]
        selHorz = [max(coord[1]-1, 0), min(coord[1]+(orient==1)*(shipLen-1)+2, 10)]
        if shipMap[selVert[0]:selVert[1], selHorz[0]:selHorz[1]].any(): 
          valid = False
      # end: Ship valid
      
      if valid:
        # Current ship could be correctly placed
        shipMap[coord[0]:coord[0]+(orient==0)*(shipLen-1)+1, 
                coord[1]:coord[1]+(orient==1)*(shipLen-1)+1] = 1
        shipsSet = True
      else:
        # Not possible to set current ship in given number of tries
        shipsSet = False
        shipMap[:,:] = 0
        resetSteps += 1
        break

  # ================================ CHECK =====================================
  if not(shipsSet) and (resetSteps == maxResetTries):
    raise "ERROR> Ships could not be set"
  else:
    return 1
  # ============================================================================



def checkDestroyed(shipMap, xy):
  """Checks if bombing the position xy results in an ship to be sunk.
  Input:
    shipMap:    numpy.array (as reference, standard) specifying the state of
                each tile in a binary fassion:
                  0: Nothing
                  1: Undestroyed part of ship
                  2: Bombed water
                  3: Destroyed ship
    xy:         list or numpy.array giving [Row, Column] of attack
  """
  if (shipMap[xy[0], xy[1]]%2 == 0):
    # No hit at all
    return 0
  # =========================== GET ORIENTATION ================================
  if   (xy[0] == 9):
    # Hit on lower field border
    surr = np.array([-1])
  elif (xy[0] == 0):
    # Hit on upper field border
    surr = np.array([1])
  else:
    surr = np.array([-1, 1])
    
  if ( (shipMap[xy[0] + surr, xy[1]]%2).any() ):
    # Ship is placed vertically
    itVec = [1, 0]
    xOrient = xy[0]
  else:
    # Ship is placed horizontally
    itVec = [0, 1]
    xOrient = xy[1]
    
  # ======================== GET SHIP SURROUNDING ==============================
  selSurr  = np.arange(max(-5, -xOrient), min(5, 9-xOrient)+1, 1, dtype='int')
  fixPos = min(5, xOrient)
  surr = shipMap[xy[0] + itVec[0]*selSurr, xy[1] + itVec[1]*selSurr]
  waterArea  = (surr%2==0).nonzero()[0]
  intactShip = (surr==1).nonzero()[0]
  dest = [False, False]
  shipStartEnd = [-1, -1]
  
  # ========================= CHECK POSITIVE SIDE ==============================
  arrWater = waterArea[waterArea > fixPos]
  arrShip  = intactShip[intactShip > fixPos]
  if   ( len(arrShip)  == 0 ):                    # No intact ship in positive half       --> pos Half destroyed
    dest[1] = True
  elif ( len(arrWater) == 0 ):                    # No water in vicinity, but intact ship --> Ship touches border and is not destroyed
    dest[1] = False
  elif ( arrWater[0] < arrShip[0] ):              # Both classes appear                   --> Compare what comes first
    dest[1] = True
  else:                                           # Only for readabilty
    dest[1] = False
    
  if ( len(arrWater) != 0):
    shipStartEnd[1] = xOrient + (arrWater[0]-fixPos)-1
  else:
    shipStartEnd[1] = 9
    

  # ========================= CHECK NEGATIVE SIDE ==============================
  arrWater = waterArea[waterArea < fixPos]
  arrShip  = intactShip[intactShip < fixPos]
  if   ( len(arrShip)  == 0 ):                    # No intact ship in negative half       --> neg Half destroyed
    dest[0] = True
  elif ( len(arrWater) == 0 ):                    # No water in vicinity, but intact ship --> Ship touches border and is not destroyed
    dest[0] = False
  elif (arrWater[-1] > arrShip[-1]):              # Both classes appear                   --> Compare what comes first
    dest[0] = True
  else:                                           # Only for readabilty
    dest[0] = False
    
  if ( len(arrWater) != 0):
    shipStartEnd[0] = xOrient + (arrWater[-1]-fixPos)+1
  else:
    shipStartEnd[0] = 0

  # =========================== MARK BOMBED AREA ===============================
  # If ship is destroyed set bombed area around ship
  if (dest[0] and dest[1]):
    if (itVec[0] == 1):
      xExt = [max(0, shipStartEnd[0]-1), min(9, shipStartEnd[1]+1)]
      yExt = [max(0, xy[1]-1), min(9, xy[1]+1)]
    else:
      xExt = [max(0, xy[0]-1), min(9, xy[0]+1)]      
      yExt = [max(0, shipStartEnd[0]-1), min(9, shipStartEnd[1]+1)]
    shipMap[xExt[0]:xExt[1]+1, yExt[0]:yExt[1]+1] = (
           shipMap[xExt[0]:xExt[1]+1, yExt[0]:yExt[1]+1]%2 + 2)
    if (debug):
      print("Ship destroyed - excluded area ({}-{}, {}-{})"
            .format(xExt[0], xExt[1], yExt[0], yExt[1]))
      print("                 Startend: {}, {}"
            .format(shipStartEnd[0], shipStartEnd[1]))
    return 1
  else:
    return 0
    
    
    
    
def parseCommand(buff, cl):
  """Parse and handle client commands
  Input:
    buff:      String containing the command to be handled
    cl:        Socket for client connection"""
  # ====================== SPLIT COMMAND IF NECESSARY ==========================
  if ((buff[0] == 'B') or (buff[0] == 'M')):
    # Position Command
    splittedBuff = buff.split(',')
    try:
      xy = [int(splittedBuff[1]), int(splittedBuff[2])]
    except:
      invalid = True
    else: 
      invalid = False
    if (max(xy)>9 or min(xy)<0 or invalid):
      cl.send("I")
      if (sent == 0):
        raise "ERROR> Sending invalid flag"
      return 'I', -1
      
  # =========================== HANDLE AND REPLY ===============================
  if   buff[0] == 'B':
    state = shipMap[xy[0], xy[1]]%2
    shipMap[xy[0], xy[1]] = state+2
    if (state):
      dest  = checkDestroyed(shipMap, xy)
    else:
      dest = 0
    sent = cl.send("R, {}, {}".format(state, dest))   # Returns R, then if it was a hit and if the ship was destroyed
    if (sent == 0):
      raise "ERROR> Sending B result failed"
    return  'B', [xy[0], xy[1], state, dest]
    
  elif buff[0] == 'M':
    state = max(1, shipMap[xy[0], xy[1]])
    if (state == 1): state = 0              # This way the bot can not derive the real state via runtime analysis
    sent = cl.send("R, {}".format(state))
    if (sent == 0):
      raise "ERROR> Sending M result failed"
    return  'M', [xy[0], xy[1], state]

  else:
    # Invalid command
    cl.send("I")
    if (sent == 0):
      raise "ERROR> Sending invalid flag"
    return 'I', -1
################################################################################





################################################################################
###                           MAIN LOOP                                      ###
################################################################################

# ========================= OPEN CONNECTION ====================================
s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12345                # Reserve a port for your service.
s.bind((host, port))        # Bind to the port
s.listen(1)                 # Now wait for 1 client connection.
cls, adds = s.accept()      # Establish connection with client.

print 'Got connection from', adds
sent = saveSend(cls, 'Y - Thank you for connecting')
if (sent == 0):
  # Handshake error
  raise "ERROR> Handshake not successfull"

# =========================== PLACE SHIPS ======================================
shipMap = np.zeros((10, 10), dtype=int)
setShipsRandom(shipMap)
print("All ships set")


if (visu):
  pp.imshow(shipMap, interpolation='None', vmin=0, vmax=3)
  pp.xlim([-0.5, 9.5])
  pp.ylim([-0.5, 9.5])
  pp.show(0)


for steps in range(1000):
  saveSend(cls, "T")
  buff = cls.recv(1024)
  if (buff == 'Y'):
    print("Round {}".format(steps))   
    for i in range(1000):
      buff = cls.recv(1024)
      if (debug):
        print("Received command: " + buff)
      act, result = parseCommand(buff, cls)
      
      if (act == 'B') and (visu):
        pp.imshow(shipMap, interpolation='None', vmin=0, vmax=3)
        pp.plot(result[1], result[0], 'ko')
        pp.xlim([-0.5, 9.5])
        pp.ylim([-0.5, 9.5])
        pp.show()
      if (act == 'B'): 
        break
  else:
    if (debug):
      print("Received unexpected command")
    saveSend(cls, "N")
  
  # Check if all ships are destroyed!
  if ( min(shipMap[shipMap%2>0]) == 3 ):
    break
  
cls.send("EOG")
print("Finished after {} steps".format(steps))
cls.close()                # Close the connection
