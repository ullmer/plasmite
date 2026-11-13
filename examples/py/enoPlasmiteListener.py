"""
Threaded callback-based Plasmite listener.
Inspired by enoPlasmaListener.py
Brygg Ullmer, Clemson University + Copilot
Begun 2026-11-11
"""

import threading
import logging
import traceback
import json
from types import SimpleNamespace

from plasmite import Client

class enoPlasmiteListener:
  poolName = None
  dataPath = "./data"
  thread   = None
  running  = False
  callback = None
  ready    = None
  tags     = None
  live_only= True

  ########### constructor ###########
  def __init__(self, **kwargs):
    self.__dict__.update(kwargs)
    self.running = False
    self.ready   = threading.Event()

    logging.basicConfig(level=logging.INFO)
    self.logger = logging.getLogger(__name__)

  ########### log error ###########
  def logErr(self, msg):
    try:    self.logger.error(msg); traceback.print_exc()
    except: print("logErr error:"); traceback.print_exc()

  ########### log info ###########
  def logInf(self, msg):
    try:    self.logger.info(msg)
    except: print("logInf error:"); traceback.print_exc()

  ########### _listen ###########
  def _listen(self):
    try:
      if self.poolName is None: 
        self.logErr("No pool name provided"); return

      try:    client    = Client(self.dataPath)
      except: self.logErr("_listen: problem creating client:"); return 

      try:    pool = client.open_pool(self.poolName) 
      except: 
        try:  pool = client.create_pool(self.poolName, 4 * 1024 * 1024)
        except: self.logErr("_listen: err creating pool " + self.poolName); return 

      self.pool = pool
      self.logger.info(f"Connected to pool {self.poolName}")
      self.ready.set()

      for msg in pool.tail(timeout_ms=None, tags=self.tags, live_only=self.live_only):
        if not self.running: break
        try:
          if self.callback: 
            if isinstance(msg.raw, bytes):
              mrd = msg.raw.decode("utf-8")
              obj = json.loads(mrd, object_hook=lambda d: SimpleNamespace(**d))
              self.callback(obj)
        except Exception: traceback.print_exc()

    except Exception:
      self.logger.error("_listen setup issue")
      traceback.print_exc()

  ########### start ###########

  def start(self):
    if not self.running:
      self.running = True
      self.thread = threading.Thread(target=self._listen, daemon=True)
      self.thread.start()

    self.ready.wait(timeout=1.0)

  ########### stop ###########

  def stop(self):
    self.running = False
    if self.thread:
      self.thread.join(timeout=1.0)
    self.logger.info("enoPlasmiteListener stopped")

  ########### append ###########

  def append(self, data, tags=None, durability=None):
    with Client(self.dataPath) as client:
      with client.open_pool(self.poolName) as pool:
        if durability is None:
          return pool.append(data, tags or [])
        return pool.append(data, tags or [], durability)

################ test harness ################

def handle_message(msg):
  print("seq :", msg.seq)
  print("tags:", msg.tags)
  print("data:", msg.data)
  print()

if __name__ == "__main__":

  listener = enoPlasmiteListener(
    poolName="grObjPool",
    tags=["gfx", "scope:sharedCanvas"],
    callback=handle_message
  )

  listener.start()

  try:
    while True: threading.Event().wait(1.0)
  except KeyboardInterrupt: listener.stop()

### end ###
