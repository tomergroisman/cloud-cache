class Node_Cache:

  def __init__(self):
    self._cache = {}

  def put(self, key, data, expiration_date):
    """Put a value to the cache"""
    self._cache[key] = {
      "data": data,
      "expiration_date": expiration_date
    }

  def get(self, key):
    """Get value from the cache"""
    data = self._cache.get(key, {}).get("data", None)
    return data

  def get_cache(self):
    """Get all instance cache"""
    return self._cache