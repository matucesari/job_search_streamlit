# scrapers/base.py

import time
import hashlib
import pickle
import redis
import random
from abc import ABC, abstractmethod

class JobScraper(ABC):
    # Token bucket config (10 requests/minute)
    tokens = 10
    last_refill = time.time()
    refill_rate = 10  # tokens per minute

    def __init__(self, proxy_pool=None):
        self.proxy_pool = proxy_pool or []
        self.current_proxy = 0
        self.results = []
        self.redis = redis.Redis(host="redis", port=6379, decode_responses=False)

    def _refill_tokens(self):
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = int(elapsed * self.refill_rate / 60)
        if tokens_to_add > 0:
            self.tokens = min(10, self.tokens + tokens_to_add)
            self.last_refill = now

    def _throttle(self):
        self._refill_tokens()
        if self.tokens <= 0:
            sleep_time = 60 / self.refill_rate
            time.sleep(sleep_time)
            self._refill_tokens()
        self.tokens -= 1

    def _get_next_proxy(self):
        if not self.proxy_pool:
            return None
        proxy = self.proxy_pool[self.current_proxy % len(self.proxy_pool)]
        self.current_proxy += 1
        return {"http": proxy, "https": proxy}

    def _make_cache_key(self, *args):
        key_raw = ":".join(map(str, args))
        return hashlib.sha256(key_raw.encode()).hexdigest()

    def get_cached(self, key):
        value = self.redis.get(key)
        return pickle.loads(value) if value else None

    def set_cache(self, key, value, ttl=3600):
        self.redis.setex(key, ttl, pickle.dumps(value))

    @abstractmethod
    def scrape(self, keywords: str, country: str, pages: int = 1):
        pass
