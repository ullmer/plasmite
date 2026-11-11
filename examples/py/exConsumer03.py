"""
Example threaded enoPlasmiteListener usage.
"""

from enoPlasmiteListener import *

import time
import sys

def handle_message(msg):
    print("SEQ :", msg.seq)
    print("DATA:", msg.data)
    print()

listener = enoPlasmiteListener(
    poolName="grObjPool",
    tags=["gfx", "scope:sharedCanvas"],
    callback=handle_message
)

listener.start()

for i in range(1000):
    print(f"{i} ", end="")
    sys.stdout.flush()
    time.sleep(1.)

listener.stop()

### end ###
