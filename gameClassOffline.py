#!/usr/bin/python           # This is client.py file
import numpy as np
import time
from server import setShipsRandom, excludeXShape, checkDestroyed


class game:
  """This class is the unsave brother of the server base game class. There is 
  an easy way to gain access to the shipMap, since it is a 'public' class
  variable. The advantage is, however, the classes speed. A round lasts
  only between 10ms and 100ms (depending on the machines power). Also rounds
  can be started in a parallel manor without the need to change the port.
  Due to this drawbacks the bot benchmark is not official!
  
  tl;dr; YES! You can hack this - but there is no advantage for you!"""
  
  ##############################################################################
  def __init__(self, host=0, port=12345, debug=False):
  ##############################################################################
    """Class providing basic for starting the game. The Arguments of the class
    are just dummies to mirror the functionality of the online class. This way
    the classes are perfectly interchangeable.
    
    Args:
      host(string):     Dummy
      port(int):        Dummy"""
    self.debug = debug
    
    self.shipMap = np.zeros((10, 10))     # Init field
    setShipsRandom(self.shipMap)
    self.isEOG       = False
    self.rounds      = 0
  # ============================================================================



  ##############################################################################
  def initRound(self):
  ##############################################################################
    """"""
    # Check if all ships are destroyed!
    if ( min(self.shipMap[self.shipMap%2>0]) == 3 ): 
      self.isEOG = True
      print("Finished after {} steps".format(self.rounds))
      return 0
    else:
      return 1    
    if (self.debug):
      print("Round {}".format(self.rounds+1))
  # ============================================================================



  ##############################################################################
  def closeConnection(self):
  ##############################################################################
    """Dummy function to allow interchangeability"""
    if (self.debug):
      print("Closed game Instance")      
  # ============================================================================



  ##############################################################################
  def estConnection(self):
  ##############################################################################
    return 1
  # ============================================================================
      
      
      
  ##############################################################################
  def saveSend(self, command):
  ##############################################################################
    return 1
  # ============================================================================
      
      
      
  ##############################################################################
  def mapRequest(self, x, y):
  ##############################################################################
    """Makes a map request and returns the state. This is one tile of the field.
    
    Args::
      x(int):    Row position
      y(int):    Col position
      
    Returns:
      int:   tile state at given position. The value corresponds to the 
            state as follows:
             * 0 - Unknown
             * 2- Allready bombed in a previous round
             * 3 - Successfull hit in a previous round"""

    if (min(x, y) < 0 and max(x, y) > 9):
      print("Invalid map request")
      return -1
    else:
      state = max(1, self.shipMap[x, y])
      if (state == 1): state = 0              # This way the bot can not derive the real state via runtime analysis
      return state
  # ============================================================================
        
        
        
  ##############################################################################
  def fieldRequest(self):
  ##############################################################################
    """Makes field request and returns the states. This is the whole game field.
    
    Args::
      x(int):    Row position
      y(int):    Col position
      
    Returns:
      int:   tile state for the complete field. The value corresponds to the 
            state as follows:
             * 0 - Unknown
             * 2- Allready bombed in a previous round
             * 3 - Successfull hit in a previous round"""

    state = np.maximum(self.shipMap, 1)
    state[state==1] = 0      # This way the bot can not derive the real state via runtime analysis
    return state



        
  ##############################################################################
  def bomb(self, x, y):
  ##############################################################################
    """Sends bomb request and returns success of bombing
    
    Args:
      x(int):    Row position
      y(int):    Col position
      
    Returns:
      int:   Hit (1) or not hit (0)
      int:   Ship destroyed (1) or not (0)"""
    if (min(x, y) < 0 and max(x, y) > 9):
      print("Invalid bomb request")
      return -1
    else: 
      state = self.shipMap[x, y]%2
      if (state):
        # The diagonal neighbors of an hit are with certainty no hit
        # --> Exclude them
        excludeXShape(self.shipMap, [x,y])
        # Check if ship is destroyed and if that is the case --> Exclude even more tiles
        dest  = checkDestroyed(self.shipMap, [x,y])
      else:
        self.shipMap[x, y] = state+2
        dest = 0
      self.rounds += 1   # Successfull round
      return  state, dest
    
  # ============================================================================
# END CLASS
