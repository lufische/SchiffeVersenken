#!/usr/bin/python           # This is client.py file
import socket               # Import socket module
import numpy as np
import time
from gameClass import *


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
    newDirection[1]=-direction[0]
  else:
    newDirection[0]=direction[1]
  return newDirection

def step(oldX,oldY,stepSize):
  x=(oldX+1)%10
  y=oldY+((oldX+1)/10)
  return x,y
  
def dist(x,y):
  buf=0
  if len(x)!=len(y):
    return 1000
  for i in range(0,len(x)):
    buf+=(x[i]-y[i])**2
  return buf

def getNewTarget(shipMap):
  maxBuf=-1
  cPos=[-1,-1]
  hitPos=[]
  minPos=cPos
  for i in range(0,10):
    for j in range(0,10):
      if shipMap[i,j]!=0:
        hitPos.append([i,j])
  for k in range(0,10):
    for l in range(0,10):
      minBuf=1000
      for a in hitPos:
        b=[k,l]
        cDist=dist(a,b)
        if(cDist<minBuf):
          minBuf=cDist
          cPos=b
      if minBuf>maxBuf:
        minPos=cPos
        maxBuf=minBuf
  if gInst.debug:
    print("Maximal distance: {} with position {},{}".format(maxBuf,minPos[0],minPos[1]))
  return minPos        
            

initialPos=[4,4]

def botRound(gInst): # THIS IS THE DETERMINISTIC BOT

  shipMap = gInst.fieldRequest()
  if (np.min(shipMap) == -1):
    raise "ERROR> Incomplete field request returned"

  success=1
  if botRound.hit==1 and botRound.dest==1:
    botRound.hitMode=False
    botRound.cx=botRound.backupX
    botRound.cy=botRound.backupY
    if gInst.debug:
      print("Exited hitmode")
  if botRound.hit==1 and botRound.dest==0:
    if botRound.hitMode:
      success=2
    else:
      botRound.hitMode=True
      botRound.backupX=botRound.cx
      botRound.backupY=botRound.cy
      if gInst.debug:
        print("Entered hitmode")
  if botRound.hit==0:
    success=0

  if botRound.hitMode:
    botRound.cx,botRound.cy=searchShip(shipMap,botRound.cx,botRound.cy,success)
  else:
    if botRound.begun:
      botRound.cx,botRound.cy=getNewTarget(shipMap)

  if gInst.debug:
    print("Targeting position: {},{}".format(botRound.cx,botRound.cy))
  botRound.hit, botRound.dest = gInst.bomb(botRound.cx,botRound.cy) 
  if (gInst.debug):
    print("Bombed - Hit: {}, dest: {}".format(botRound.hit, botRound.dest))
  botRound.begun=True
      
    # End bot Round

botRound.begun=False
botRound.cx=initialPos[0]
botRound.cy=initialPos[1]
botRound.backupX=4
botRound.backupY=4
botRound.dest=0
botRound.hit=0
botRound.hitMode=False
searchShip.status=shipStatus(-1,-1)


if __name__=="__main__":
  numHits=0
  gInst = game(debug=False)

  while not(gInst.isEOG):
    roundStatus = gInst.initRound()
    if (roundStatus == 1):
      botRound(gInst)
      numHits+=1
  print("Number of shots: {}".format(numHits))
  gInst.closeConnection()
