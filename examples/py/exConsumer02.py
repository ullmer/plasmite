from plasmite import Client, parse_message
from types import SimpleNamespace

def parse_message(raw):
  if isinstance(raw, bytes):
    msg = raw.decode("utf-8")
    obj = json.loads(msg, object_hook=lambda d: SimpleNamespace(**d))
    return(obj)

with Client("./data") as client:
  with client.open_pool("grObjPool") as pool:

    stream = pool.tail(timeout_ms=None, tags=["gfx", "scope:sharedCanvas"], live_only=True)

    for raw in stream:
      #msg = parse_message(raw)
      #print(msg)
      print(raw)

### end ###
