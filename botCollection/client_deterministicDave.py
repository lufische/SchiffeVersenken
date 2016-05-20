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

  class shipStatus:
    def __init__(self,xInit,yInit):
      self.x=[]
      self.y=[]
      self.x.append(xInit)
      self.y.append(yInit)
    def getX(self,i):
      return self.x[i]
    def getY(self,i):
      return self.y[i]
    def length(self):
      return len(self.x)
    def addTile(self,xNew,yNew):
      self.x.append(xNew)
      self.y.append(yNew)
    def verify(self,xGuess,yGuess):
      possible=0
      otherX=0
      otherY=0
      for i in range(0,len(self.x)):
        if(xGuess!=self.x[i]):
          otherX+=1
        if(yGuess!=self.y[i]):
          otherY+=1
      if (otherX>1 and otherY>0) or (otherY>0 and otherX>1):
        possible=1
      return possible
    

  def searchShip(shipMap,oldX,oldY,lastSuccess):
    if lastSuccess==1:
      searchShip.status=shipStatus(oldX,oldY)
    if lastSuccess==2:
      searchShip.status.addTile(oldX,oldY)
    size=searchShip.status.length()
    direction=[1,0]
    cstate=1
    targetFound=False
    shipIndices=range(0,size)
    shipIndices.reverse()
    for i in shipIndices:
      for j in range(0,4):
        cx=searchShip.status.getX(i)
        cy=searchShip.status.getY(i)
        x=cx+direction[0]
        y=cy+direction[1]
        if x>9 or y>9 or x<0 or y<0:
          cstate=1
          direction=nextDirection(direction)
        else:
          cstate=shipMap[x,y]
          cstate+=searchShip.status.verify(x,y)
          if cstate==0:
            targetFound=True
            break
          direction=nextDirection(direction)
      if targetFound:
        break
    return x,y
      

  def nextDirection(direction):
    newDirection=[0,0]
    if direction[0]!=0:
      newDirection[1]=direction[0]
      direction[0]=0
    else:
      newDirection[0]=-direction[1]
      newDirection[1]=0
    return newDirection

  def step(oldX,oldY,stepSize):
    x=(oldX+1)%10
    y=oldY+((oldX+1)/10)
    return x,y

  def getNewTarget(shipMap,oldX,oldY,lastX,lastY):
    cstate=1
    stepSize=2
    x=oldX
    y=oldY
    i=0
    #game ends only after getNewTarget() has been executed -> terminate if all fields are bombed
    while cstate!=0 and i<100:
      i+=1
      x,y=step(x,y,stepSize)
      x=x%10
      y=y%10
      cstate=shipMap[x,y]
      if x==lastX and y==lastY:
        cstate=1
      if debug:
        print("At position {},{} with status {}".format(x,y,cstate))
      stepSize=1
    return x,y

  def botRound(sock): # THIS IS THE DETERMINISTIC BOT

    shipMap = fieldRequest(sock)
    if (np.min(shipMap) == -1):
      raise "ERROR> Incomplete field request returned"

    if debug:
      print("Targeting position: {},{}".format(botRound.cx,botRound.cy))
    hit, dest = bomb(sock,botRound.cx,botRound.cy) 
    if (debug):
      print("Bombed - Hit: {}, dest: {}".format(hit, dest))

    lastX=botRound.cx
    lastY=botRound.cy
    success=1
    if hit==1 and dest==1:
      botRound.hitMode=False
      botRound.cx=botRound.backupX
      botRound.cy=botRound.backupY
      if debug:
        print("Exited hitmode")
    if hit==1 and dest==0:
      if botRound.hitMode:
        success=2
      else:
        botRound.hitMode=True
        botRound.backupX=botRound.cx
        botRound.backupY=botRound.cy
        if debug:
          print("Entered hitmode")
    if hit==0:
      success=0

    if botRound.hitMode:
      botRound.cx,botRound.cy=searchShip(shipMap,botRound.cx,botRound.cy,success)
    else:
      botRound.cx,botRound.cy=getNewTarget(shipMap,botRound.cx,botRound.cy,lastX,lastY)
      
    # End bot Round

  botRound.cx=1
  botRound.cy=0
  botRound.backupX=1
  botRound.backupY=0
  botRound.hitMode=False
  searchShip.status=shipStatus(-1,-1)


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

  numHits=0
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
      numHits+=1
    elif (buff == "EOG"):
      print("End of game")
      print("Number of hits: {}".format(numHits))
      isEOG = True
    elif (buff[0] == "N"):
      print("Unsynced client behaviour")

  sock.close()                     # Close the socket when done
