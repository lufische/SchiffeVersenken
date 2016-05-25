#!/usr/bin/python           # This is client.py file
import socket               # Import socket module
import numpy as np
import time
import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from gameClass import *     # imports game class


# ============================= INIT BOT =======================================
# You can init your bot here
nnorm=0.1
borderparameter=0 #borderparameter 1 means borders are ships, borderparameter 0 means borders are unknown
rangeparameter=1 #1 is good
def choose_aim(array):
  global nnorm
  global borderparameter
  global rangeparameter
  field=np.ones((12,12))
  field=field*2
  field[1:11,1:11]=array
  #check if there are already localized ships
  #direction is known
  for i in range(1,11):
    for j in range(1,11):
      if field[i,j]==3 and field[i+1,j]==0 and field[i-1,j]==3:
	return [i-1+1,j-1]
      elif field[i,j]==3 and field[i,j+1]==0 and field[i,j-1]==3:
	return [i-1,j-1+1]
      elif field[i,j]==3 and field[i,j-1]==0 and field[i,j+1]==3:
	return [i-1,j-1-1]
      elif field[i,j]==3 and field[i-1,j]==0 and field[i+1,j]==3:
	return [i-1-1,j-1]	
  #direction is known
  for i in range(1,11):
    for j in range(1,11):	
      if field[i,j]==3 and field[i+1,j]==0:
	return [i-1+1,j-1]
      elif field[i,j]==3 and field[i,j+1]==0:
	return [i-1,j-1+1]
      elif field[i,j]==3 and field[i,j-1]==0:
	return [i-1,j-1-1]
      elif field[i,j]==3 and field[i-1,j]==0:
	return [i-1-1,j-1]	
  #when there are no localized ships but a little space
  field=np.ones((14,14))
  if borderparameter==1:
    field[1:13,1:13]=np.zeros((12,12))
  field[2:12,2:12]=array
  field_evaluation=np.zeros((10,10))   
  for i1 in range(0,10):
    for j1 in range(0,10):
      if field[i1+2,j1+2]==0:
	field_evaluation[i1,j1]=100000000000000
	for i2 in range(0,14):
	  for j2 in range(0,14):
	    if not (i2==i1+2 and j2==j1+2) and not field[i2,j2]==0:
	      dist=np.power(np.absolute(i2-(i1+2)),nnorm)+np.power(np.absolute(j2-(j1+2)),nnorm)#dsquared
	      if dist<field_evaluation[i1,j1]:
		field_evaluation[i1,j1]=dist
  #when there but no space
  if np.amax(field_evaluation)>rangeparameter:
    return [int(np.floor(np.argmax(field_evaluation)/10)),np.argmax(field_evaluation)%10]  
  else:
    field=np.ones((20,20))
    field[5:15,5:15]=array
    field_evaluation=np.zeros((10,10))  
    for i1 in range(0,10):
      for j1 in range(0,10):
	if field[i1+5,j1+5]==0:
	    if field[i1+5+1,j1+5]==0 or field[i1+5-1,j1+5]==0 or field[i1+5,j1+5+1]==0 or field[i1+5,j1+5-1]==0:
	      field_evaluation[i1,j1]=2
	      if (field[i1+5+1,j1+5]==0 and field[i1+5-1,j1+5]==0) or (field[i1+5,j1+5+1]==0 and field[i1+5,j1+5-1]==0):
		field_evaluation[i1,j1]=3    
		if (field[i1+5+2,j1+5]==0 and field[i1+5-2,j1+5]==0) or (field[i1+5,j1+5+2]==0 and field[i1+5,j1+5-2]==0):
		  field_evaluation[i1,j1]=5
		  if (field[i1+5+3,j1+5]==0 and field[i1+5-3,j1+5]==0) or (field[i1+5,j1+5+3]==0 and field[i1+5,j1+5-3]==0):
		    field_evaluation[i1,j1]=7
		    if (field[i1+5+4,j1+5]==0 and field[i1+5-4,j1+5]==0) or (field[i1+5,j1+5+4]==0 and field[i1+5,j1+5-4]==0):
		      field_evaluation[i1,j1]=9 
		      if (field[i1+5+5,j1+5]==0 and field[i1+5-5,j1+5]==0) or (field[i1+5,j1+5+5]==0 and field[i1+5,j1+5-5]==0):
			field_evaluation[i1,j1]=11		
	      
    return [int(np.floor(np.argmax(field_evaluation)/10)),np.argmax(field_evaluation)%10]
    
def botRound(gInst): # THIS IS THE RANDOM BOT
  tileFound = False
  shipMap = gInst.fieldRequest()
  if (np.min(shipMap) == -1):
    raise "ERROR> Incomplete field request returned"
  
  target = choose_aim(shipMap)
  hit, dest = gInst.bomb(target[0], target[1])                  # Bomb map
  if (gInst.debug):
    print("Bombed - Hit: {}, dest: {}".format(hit, dest))
  # End bot Round


if __name__=="__main__":
  gInst = game(debug=False)

  while not(gInst.isEOG):
    roundStatus = gInst.initRound()
    if (roundStatus == 1):
      botRound(gInst)
  gInst.closeConnection()
