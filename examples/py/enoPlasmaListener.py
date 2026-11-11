# Threaded, callback-based PlasmaListener code
# Original co-implemented by CoPilot and Brygg Ullmer, Clemson University
# Begun 2025-06-08

import threading
import logging
import plasma
import time
import traceback

################ PlasmaListener ################ 

class enoPlasmaListener:
  poolName,  hose,  thread = [None]*3
  running, callback, ready = [None]*3
  checkinInterval          = .03 # should change depending upon particulars

  #### constructor ####

  def __init__(self, **kwargs):
    self.__dict__.update(kwargs) #allow class fields to be passed in constructor
    self.running   = False
    self.ready     = threading.Event()

    logging.basicConfig(level=logging.INFO)
    self.logger = logging.getLogger(__name__)

  #### deposit ####

  def deposit(self, protein):
    if self.hose is None: self.logger.error(f"deposit: no hose"); return
    try:    return self.hose.Deposit(protein)
    except: self.logger.error(f"deposit error"); traceback.print_exc()

  #### _listen ####

  def _listen(self):
    try:
      if self.poolName is None: self.logger.error(f"No pool name provided!"); return

      self.hose = plasma.Pool.Participate(self.poolName)

      if self.hose is None: self.logger.error(f"Failed to connect to pool: {self.poolName}"); return

      self.logger.info("Connected to pool, listening for messages...")
      self.ready.set()
    except: self.logger.error(f"_listener setup issue caught")

    try:
      while self.running:
        #protein = self.hose.Next(-1)
        protein = self.hose.Next(self.checkinInterval)
        if protein.IsNull(): continue
        if self.callback:    self.callback(protein)
    finally:
      self.hose.Withdraw()

  #### start ####

  def start(self):
    if not self.running:
      self.running = True
      self.thread  = threading.Thread(target=self._listen, daemon=True)
      self.thread.start()
      self.logger.info("enoPlasmaListener started")
    self.ready.wait(timeout=1.0)
  
  #### stop ####

  def stop(self):
    self.running = False
    if self.thread:
      self.thread.join()
      self.logger.info("PlasmaListener stopped")

################## Test harness ################## 

def handle_message(protein):
  d, i = protein.Descrips(), protein.Ingests()
  print("d ->", d.ToString())
  print("i ->", i.ToString())

if __name__ == "__main__":
  listener = enoPlasmaListener(poolName="tcp://localhost/hello", callback=handle_message)
  listener.start()
  listener.ready.wait(timeout=1.0)
  time.sleep(0.5)

  try:
    while True: time.sleep(0.1)
  except KeyboardInterrupt:
    listener.stop()

### end ###
