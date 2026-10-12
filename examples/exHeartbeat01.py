import json
import time
import sys

from plasmite import Client, Durability

POOL_NAME = "grObjPool"

def open_or_create(client: Client, pool_name: str):
  try:
    return client.open_pool(pool_name)
  except Exception:
    return client.create_pool(pool_name, 4 * 1024 * 1024)

def main():
  client = Client("./data")
  pool   = open_or_create(client, POOL_NAME) 

  print(f"depositing in {POOL_NAME}")

  i = 0
  tags = ["hb"]  # heartbeat

  while True:
    protein = {"descrips": ["hb"], "ingests": i }
    payload = json.dumps(protein).encode("utf-8")

    print(json.dumps(protein))
    receipt = pool.append_json(payload, tags, Durability.FAST,)

    #print(receipt.decode("utf-8"))

    time.sleep(10)
    i += 1

if __name__ == "__main__":
  main()

### end ###
