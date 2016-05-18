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

  class aim_position():
      def __init__(self,x,y,gLat):
          self.x=x
          self.y=y
          self.nR=gLat[x+1,y]
          self.nT=gLat[x,y+1]
          self.nL=gLat[x-1,y]
          self.nB=gLat[x,y-1]
          self.nnR=gLat[x+2,y]
          self.nnT=gLat[x,y+2]
          self.nnL=gLat[x-2,y]
          self.nnB=gLat[x,y-2]
          self.ns=np.count_nonzero(np.array([self.nR,self.nT,self.nL,self.nB])==3)
          self.nw=np.count_nonzero(np.array([self.nR,self.nT,self.nL,self.nB])==2)
          
      def nnship(self):
          if (self.nR==self.nnR) and (self.nR==3):
              return 1
          elif (self.nT==self.nnT) and (self.nT==3):
              return 1
          elif (self.nL==self.nnL) and (self.nL==3):
              return 1
          elif (self.nB==self.nnB) and (self.nB==3):
              return 1
          else:
              return 0

      def classifier(self):
          para=np.array([[[5,0],[4,0],[2,0],[1,0],[0,0]],[[7,10],[6,10],[5.5,10],[4.5,10],[0,0]],[[8.5,10],[7.5,10],[7.5,10],[0,10],[0,0]],[[9,10],[8.5,10],[0,0],[0,0],[0,0]],[[10,10],[0,0],[0,0],[0,0],[0,0]]])
          return (para[self.ns,self.nw,self.nnship()])**15

  def choose_aim(array):
      
      arr=np.column_stack([np.full((array.shape[0]),2,dtype=float), array , np.full((array.shape[0]),2,dtype=float)])
      b=np.full((arr.shape[1]),2,dtype=float)
      arr=np.insert(arr,0, b, axis=0)
      arr=np.insert(arr,array.shape[0]+1, b, axis=0)
      parr=np.zeros((arr.shape[0],arr.shape[1]))
      
      arr=np.column_stack([np.full((arr.shape[0]),2,dtype=float), arr,np.full((arr.shape[0]),2,dtype=float)])
      b=np.full((arr.shape[1]),2,dtype=float)
      arr=np.insert(arr,0, b, axis=0)
      arr=np.insert(arr,arr.shape[0], b, axis=0)
      parr=np.zeros((arr.shape[0],arr.shape[1]))
      
      summe=0.0

      for i in range(2,12):
          for j in range(2,12):
              if (arr[i,j]==3) or (arr[i,j]==2):
                  parr[i,j]=0
              else:
                  aim=aim_position(i,j,arr)
                  parr[i,j]=float(aim.classifier())
              summe+=parr[i,j]
      parr=parr/summe
      
      pges=0
      p=[0,0]
      rand=np.random.random()
      for i in range(2,12):
          for j in range(2,12):
              pges+=parr[i,j]

              if rand<pges:
                  p[0]=i-2
                  p[1]=j-2
                  break
          if rand<pges:
              break

      return p


  def botRound(sock): # THIS IS THE RANDOM BOT
    i = 0
    tileFound = False
    shipMap = fieldRequest(sock)
    if (np.min(shipMap) == -1):
      raise "ERROR> Incomplete field request returned"
    
    target = choose_aim(shipMap)
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
