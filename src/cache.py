class Node_Cache:

    def __init__(self):
        self._cache = {}

    def put(self, n_bucket, key, data, expiration_date):
        """Put a value to the cache"""
        bucket = self._cache.get(n_bucket, {})
        self._cache[n_bucket] = {
            **bucket,
            key: {
                "data": data,
                "expiration_date": expiration_date
            }
        }

    def put_bucket(self, n_bucket, bucket_data):
        """Put a bucket to the cache"""
        self._cache[n_bucket] = bucket_data

    def get(self, n_bucket, key):
        """Get value from the cache"""
        data = self._cache.get(n_bucket, {}).get(key, {}).get("data", None)
        return data

    def get_cache(self):
        """Get all instances in cache"""
        return self._cache

    def put_cache(self, cache):
        """Put all instances in cache"""
        self._cache = {
            **self._cache,
            **cache
        }
        return self._cache

    def delete(self, n_bucket):
        """Delete and send bucket from cache"""
        return self._cache.pop(n_bucket, None)
