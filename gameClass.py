#!/usr/bin/python           # This is client.py file
import socket               # Import socket module
import numpy as np
import time


class game:
  ##############################################################################
  def __init__(self, host=0, port=12345, debug=False):
  ##############################################################################
    """Class providing basic functions for handling server communication
    
    Args:
      host(string):     Host Adress
      port(int):        Port for connection"""
    if (host==0): self.host = socket.gethostname() # Default: Get local machine name
    else:         self.host = host
    self.port = port                               # Reserve a port for your service.
    self.debug = debug
    
    # ======================== CONNECT TO SERVER ===================================
    res, self.sock = self.estConnection()
    if (res == 0):
      raise "ERROR> Connection could not be established"
    self.isConnected = True
    self.isEOG       = False
  # ============================================================================



  ##############################################################################
  def initRound(self):
  ##############################################################################
    buff = self.sock.recv(2048)        # Receive "T" string to start term
    if (self.debug):
      print("Init Round - Server answer: " + buff)
    if (buff == 'T'):
      res = self.saveSend('Y')   # Answer with string "Y"
      # -------------------- START OF ROUND --------------------------------------
      if (res and self.debug):
        print('==== TURN START ===')  
      return 1
    elif (buff == "EOG"):
      print("End of game")
      self.isEOG = True
      return 0
    elif (buff[0] == "N"):
      print("Unsynced client behaviour")
      return -1
  # ============================================================================



  ##############################################################################
  def closeConnection(self):
  ##############################################################################
    if (self.isConnected):
      self.sock.close()        # Receive "T" string to start term
      self.isConnected = False
      if (self.debug):
        print("Closed server connection")      
  # ============================================================================



  ##############################################################################
  def estConnection(self):
  ##############################################################################
    """Establishes connection to the server
      
    Returns:
      int: success: 1 if successfull"""
    sock = socket.socket()         # Create a socket object
    sock.connect((self.host, self.port))
    buff = sock.recv(2048)          # Handshake positive
    if (buff[0] == 'Y'):
      # Handshake positive
      print(buff[1:])
      return 1, sock
    else:
      return 0, None
  # ============================================================================
      
      
      
  ##############################################################################
  def saveSend(self, command):
  ##############################################################################
    """Sends the command to the server and checks if the command
    was submitted correctly
    
    Args:
      command(string): command
      
    Returns:
      int:          successfull. Raises error if not."""
    sent = self.sock.send(command)
    for i in range(10):
      if (sent != len(command)) and self.debug:
        print('ERROR> During sending - Retry')
      else:      
        time.sleep(0.0005) # To maintain synchronisation
        return 1
    if (sent != len(command)):
      raise "ERROR> No communication with server possible"
      return 0
  # ============================================================================
      
      
      
  ##############################################################################
  def mapRequest(self, x, y):
  ##############################################################################
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
    res = self.saveSend("M, {}, {}".format(x, y))

    # =============================== PARSE INPUT ================================+
    buff = self.sock.recv(2048)        # Get Result
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
      print("ERROR> Unexpected server string")
      print(">>>" + buff)
      return -1
  # ============================================================================
        
        
        
  ##############################################################################
  def fieldRequest(self):
  ##############################################################################
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
    res = self.saveSend("F")

    # =============================== PARSE INPUT ================================+
    buff = self.sock.recv(2048)        # Get Result
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
      print("ERROR> Unexpected server string")
      print(">>>" + buff)
      return -1
  # ============================================================================



        
  ##############################################################################
  def bomb(self, x, y):
  ##############################################################################
    """Sends bomb request and parses return
    
    Args:
      x(int):    Row position
      y(int):    Col position
      
    Returns:
      int:   Hit (1) or not hit (0)
      int:   Ship destroyed (1) or not (0)"""
    # =============================== SEND COMMAND ================================
    res = self.saveSend("B, {}, {}".format(x, y))

    # =============================== PARSE INPUT ================================+
    buff = self.sock.recv(2048)        # Get Result
    splittedBuff = buff.split(',')
    if   splittedBuff[0] == 'I': 
      print('ERROR> Invalid Command')
      return -1, -1
    elif splittedBuff[0] == 'R':
      try:    
        res  = int(splittedBuff[1])
        dest = int(splittedBuff[2])
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
  # ============================================================================
# END CLASS
