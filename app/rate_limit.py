import time

class RateLimiter:
    def __init__(self, client, limit=30, window_seconds=60):
        self.client = client
        self.limit = limit
        self.window_seconds = window_seconds

    def allow(self, identity):
        bucket = int(time.time() // self.window_seconds)
        key = f"gateway:rl:{identity}:{bucket}"
        count = self.client.incr(key)
        if count == 1:
            self.client.expire(key, self.window_seconds)
        return count <= self.limit
