"""
Example threaded enoPlasmiteListener usage.
"""

from enoPlasmiteListener import *

import time
import sys

def handleMsg(msg):
  #print("SEQ :", msg.seq)
  #print("dir:", dir(msg))
  #print("DATA:", msg.data)
  print("\nmsg:", str(msg))

listener = enoPlasmiteListener(poolName="grObjPool", tags=["gfx", "scope:sharedCanvas"],
  callback=handleMsg)

listener.start()

for i in range(1000):
  print(f"{i} ", end="")
  sys.stdout.flush()
  time.sleep(1.)

listener.stop()

### end ###
