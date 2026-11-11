"""
Minimal producer in a plasma style
- Writes JSON object payloads with tags to a local Plasmite pool.
- Uses local pool refs only (no tcp:// pool URI).
"""
import json
from plasmite import Client, Durability

def open_or_create(client: Client, pool_name: str):
  try:
    return client.open_pool(pool_name)
  except Exception:
    return client.create_pool(pool_name, 4 * 1024 * 1024)

def main() -> None:
  with Client("./data") as client:
    with open_or_create(client, "grObjPool") as pool:
      tags = ["gfx", "scope:sharedCanvas"]
      protein = {"scope": "sharedCanvas", "updates": ["sq1", "move", [10, 10]]}
      receipt = pool.append_json(
        json.dumps(protein).encode("utf-8"),
        tags,
        Durability.FAST,
      )
      #print(receipt.decode("utf-8"))

if __name__ == "__main__":
  main()
