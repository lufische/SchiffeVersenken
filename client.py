#!/usr/bin/python           # This is client.py file

# Flag to allow offline benchmarking (without server)
offlineBenchmark = True

import numpy as np
if (offlineBenchmark):
  from gameClassOffline import *     # imports game class
else:
  from gameClass        import *     # imports game class


# ============================= INIT BOT =======================================
# You can init your bot here
def botRound(gInst): # THIS IS THE RANDOM BOT
  """Import your bot in this function. As input you get an instance of the game
  class which provides bomb and fieldRequst functions.
  
  Args:
    gInst(game):     Connected game class instance"""
  shipMap = gInst.fieldRequest()
    
  tileFound = False
  while not(tileFound):
    target = [np.random.randint(10), np.random.randint(10)]     # Draw random numbers
    res = shipMap[target[0], target[1]]                         # Request map
    if (res == 0):
      tileFound = True
    elif (gInst.debug):
      print("Target position has allready been bombed - select new target")
  hit, dest = gInst.bomb(target[0], target[1])                  # Bomb map
  if (gInst.debug):
    print("Bombed - Hit: {}, dest: {}".format(hit, dest))
# End bot Round


def main():
  gInst = game(debug=False)

  while not(gInst.isEOG):
    roundStatus = gInst.initRound()
    if (roundStatus == 1):
      botRound(gInst)
  gInst.closeConnection()

if __name__=="__main__":
  main()
