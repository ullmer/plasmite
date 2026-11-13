"""
Example threaded enoPlasmiteListener usage.
"""

from enoPlasmiteListener import *

import time
import sys

def handleMsg(msg):
  print("\nSEQ :", msg.seq)
  print("DATA:",   msg.data)

listener = enoPlasmiteListener(poolName="grObjPool", tags=["gfx", "scope:sharedCanvas"],
  callback=handleMsg, live_only=True)

listener.start()

for i in range(1000):
  print(f"{i} ", end="")
  sys.stdout.flush()
  time.sleep(1.)

listener.stop()

### end ###
