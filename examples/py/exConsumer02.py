import json
from plasmite import Client, parse_message
from types    import SimpleNamespace

def parse_message(raw):
  msg = raw.decode("utf-8")
  obj = json.loads(msg, object_hook=lambda d: SimpleNamespace(**d))
  return(obj)

with Client("./data") as client:
  with client.open_pool("grObjPool") as pool:

    stream = pool.tail(timeout_ms=None, tags=["gfx", "scope:sharedCanvas"], live_only=True)
    #stream = pool.tail(timeout_ms=None, tags=["gfx", "scope:sharedCanvas"])

    for m in stream:
      msg = parse_message(m.raw)
      print(msg)

### end ###
