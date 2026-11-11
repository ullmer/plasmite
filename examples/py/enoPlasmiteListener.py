"""
Threaded callback-based Plasmite listener.

Inspired by enoPlasmaListener.py
Brygg Ullmer + Copilot
2026-11-11
"""

import threading
import logging
import traceback

from plasmite import Client

class enoPlasmiteListener:

  poolName = None
  dataPath = "./data"

  thread = None
  running = False

  callback = None
  ready = None

  tags = None

  def __init__(self, **kwargs):

    self.__dict__.update(kwargs)

    self.running = False
    self.ready   = threading.Event()

    logging.basicConfig(level=logging.INFO)
    self.logger = logging.getLogger(__name__)

  #### _listen ####

  def _listen(self):

    try:

      if self.poolName is None:
        self.logger.error("No pool name provided")
        return

      with Client(self.dataPath) as client:

        with client.open_pool(self.poolName) as pool:

          self.pool = pool

          self.logger.info(
            f"Connected to pool {self.poolName}"
          )

          self.ready.set()

          for msg in pool.tail(
              timeout_ms=None,
              tags=self.tags):

            if not self.running:
              break

            try:
              if self.callback:
                self.callback(msg)

            except Exception:
              traceback.print_exc()

    except Exception:

      self.logger.error("_listen setup issue")
      traceback.print_exc()

  #### start ####

  def start(self):

    if not self.running:

      self.running = True

      self.thread = threading.Thread(
        target=self._listen,
        daemon=True
      )

      self.thread.start()

    self.ready.wait(timeout=1.0)

  #### stop ####

  def stop(self):

    self.running = False

    if self.thread:
      self.thread.join(timeout=1.0)

    self.logger.info("enoPlasmiteListener stopped")

  #### append ####

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
    while True:
      threading.Event().wait(1.0)

  except KeyboardInterrupt:
    listener.stop()

### end ###
