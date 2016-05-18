#!/usr/bin/python           # This is client.py file
import socket               # Import socket module
import numpy as np
import time


debug = False

################################################################################
###                        HELPER FUNCTIONS                                  ###
################################################################################
def estConnection(host, port):
  """Establishes connection to the server
  
  Args:
    host(string):     Host Adress
    port(int):     Port for connection
    
  Returns:
    int: success: 1 if successfull"""
  sock = socket.socket()         # Create a socket object
  sock.connect((host, port))
  buff = sock.recv(2048)          # Handshake positive
  if (buff[0] == 'Y'):
    # Handshake positive
    print(buff[1:])
    return 1, sock
  else:
    return 0, None
    
    
    
def saveSend(sock, command):
  """Sends the command to the server and checks if the command
  was submitted correctly
  
  Args:
    command(string): command
    
  Returns:
    int:          successfull. Raises error if not."""
  sent = sock.send(command)
  for i in range(10):
    if (sent != len(command)) and debug:
      print('ERROR> During sending - Retry')
    else:      
      time.sleep(0.0005) # To maintain synchronisation
      return 1
  if (sent == 0):
    raise "ERROR> No communication with server possible"
    return 0
    
    
    
    
def mapRequest(sock, x, y):
  """Sends map request and parses return. This is one tile of the field.
  
  Args::
    x(int):    Row position
    y(int):    Col position
    
  Returns:
    int:   tile state at given position. The value corresponds to the 
          state as follows:
           * 0 - Unknown
           * 2- Allready bombed in a previous round
           * 3 - Successfull hit in a previous round"""
  # =============================== SEND COMMAND ================================
  res = saveSend(sock, "M, {}, {}".format(x, y))

  # =============================== PARSE INPUT ================================+
  buff = sock.recv(2048)        # Get Result
  splittedBuff = buff.split(',')
  if   splittedBuff[0] == 'I': 
    print('ERROR> Invalid Command')
    return -1
  elif splittedBuff[0] == 'R':
    try:    res = int(splittedBuff[1])
    except:
      raise "Error> Server returned non int result on Map request"
      return -1
    else:
      return res
  elif splittedBuff[0] == 'T' or splittedBuff[0] == 'N':
    print("Turn not initialated")
    return -1
  else:
    print(">>>" + buff)
    raise "ERROR> Unexpected server string"
      
      
      
      
      
def fieldRequest(sock):
  """Sends field request and parses return. This is the whole game field.
  
  Args::
    x(int):    Row position
    y(int):    Col position
    
  Returns:
    int:   tile state for the complete field. The value corresponds to the 
          state as follows:
           * 0 - Unknown
           * 2- Allready bombed in a previous round
           * 3 - Successfull hit in a previous round"""
  # =============================== SEND COMMAND ================================
  res = saveSend(sock, "F")

  # =============================== PARSE INPUT ================================+
  buff = sock.recv(2048)        # Get Result
  splittedBuff = buff.split(',')
  if   splittedBuff[0] == 'I': 
    print('ERROR> Invalid Command')
    return -1
  elif splittedBuff[0] == 'R':
    shipMap = np.zeros((100,))-1
    for i in range(100):
      try: shipMap[i] = int(splittedBuff[1+i]) 
      except:
        raise "Error> Server returned non int result on Map request"
        return shipMap.reshape(10, 10)
    return shipMap.reshape(10, 10)
  elif splittedBuff[0] == 'T' or splittedBuff[0] == 'N':
    print("Turn not initialated")
    return -1
  else:
    print(">>>" + buff)
    raise "ERROR> Unexpected server string"




      
      
def bomb(sock, x, y):
  """Sends bomb request and parses return
  
  Args:
    x(int):    Row position
    y(int):    Col position
    
  Returns:
    int:   Hit (1) or not hit (0)
    int:   Ship destroyed (1) or not (0)"""
  # =============================== SEND COMMAND ================================
  res = saveSend(sock, "B, {}, {}".format(x, y))

  # =============================== PARSE INPUT ================================+
  buff = sock.recv(2048)        # Get Result
  splittedBuff = buff.split(',')
  if   splittedBuff[0] == 'I': 
    print('ERROR> Invalid Command')
    return -1, -1
  elif splittedBuff[0] == 'R':
    try:    
      res = int(splittedBuff[1])
      dest = int(splittedBuff[1])
    except:
      raise "Error> Server returned non int result on bomb request"
      return -1, -1
    else:
      return res, dest
  elif splittedBuff[0] == 'T' or splittedBuff[0] == 'N':
    print("Turn not initialated")
    return -1, -1
  else:
    raise "ERROR> Unexpected server string"
    
if __name__=="__main__":
  ################################################################################
  ###                                MAIN                                      ###
  ################################################################################

  # ======================== CONNECT TO SERVER ===================================
  host = socket.gethostname() # Get local machine name
  port = 12345                # Reserve a port for your service.
  res, sock = estConnection(host, port)
  time.sleep(0.0005)
  if (res == 0):
    raise "ERROR> Connection could not be established"


# ============================= INIT BOT =======================================
# You can init your bot here
def botRound(sock): # THIS IS THE RANDOM BOT
  i = 0
  tileFound = False
  shipMap = fieldRequest(sock)
  if (np.min(shipMap) == -1):
    raise "ERROR> Incomplete field request returned"
    
  while i<1000 and not(tileFound):
    target = [np.random.randint(10), np.random.randint(10)]     # Draw random numbers
    res = shipMap[target[0], target[1]]                         # Request map
    if (res == 0):
      tileFound = True
    elif (debug):
      print("Target position has allready been bombed - select new target")
  hit, dest = bomb(sock, target[0], target[1])                  # Bomb map
  if (debug):
    print("Bombed - Hit: {}, dest: {}".format(hit, dest))
  # End bot Round



# ============================ PLAY ROUND ======================================
# Handshake concept:
# Server:  Initiates turn with string "T"
# Client:  Answers with string "Y"
#
# After that the client can send up to 999 map requests
#       and can start one bomb
# After bombing the client must reinitiate the new turn as described above
#
# The game is terminated from the server by sending the string "EOG".
#
# Please ensure, that all steps of the handshake is correctly implemented in 
# the client. If that is not the case, you will run in an unsynced behaviour 
# and therefore a dead-loop

isEOG = False
while not(isEOG):
  buff = sock.recv(2048)        # Receive "T" string to start term
  if (buff == 'T'):
    res = saveSend(sock, 'Y')   # Answer with string "Y"
    # -------------------- START OF ROUND --------------------------------------
    if (debug):
      print('==== TURN START ===')
    # ---------------- IMPLEMENT YOUR BOT HERE ---------------------------------
    botRound(sock)
  elif (buff == "EOG"):
    print("End of game")
    isEOG = True
  elif (buff[0] == "N"):
    print("Unsynced client behaviour")

sock.close()                     # Close the socket when done
