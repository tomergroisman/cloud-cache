class Node_Cache:

  def __init__(self):
    self.cache = {}

  def put(self, key, data, expiration_date):
    self.cache[key] = {
      "data": data,
      "expiration_date": expiration_date
    }

  def get(self, key):
    print(self.cache)
    data = self.cache.get(key, {}).get("data", None)
    print(data)
    return data