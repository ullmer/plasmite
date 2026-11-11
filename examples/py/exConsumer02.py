from plasmite import Client, parse_message

with Client("./data") as client:
  with client.open_pool("grObjPool") as pool:

    stream = pool.tail(
      timeout_ms=None,
      tags=["gfx", "scope:sharedCanvas"]
    )

    for raw in stream:
      msg = parse_message(raw)
      print(msg["data"])

### end ###
