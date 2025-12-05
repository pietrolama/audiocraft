from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict
import time


class TokenBucket:
    """Simple token bucket rate limiter"""
    
    def __init__(self, max_tokens: int, refill_period_seconds: int):
        self.max_tokens = max_tokens
        self.refill_period = refill_period_seconds
        self.tokens: Dict[str, float] = defaultdict(lambda: max_tokens)
        self.last_refill: Dict[str, float] = defaultdict(time.time)
    
    def is_allowed(self, key: str) -> tuple[bool, int]:
        """
        Check if request is allowed for key
        Returns (is_allowed, tokens_remaining)
        """
        now = time.time()
        last = self.last_refill[key]
        
        # Refill tokens
        elapsed = now - last
        if elapsed >= self.refill_period:
            self.tokens[key] = self.max_tokens
            self.last_refill[key] = now
        else:
            # Refill proportionally
            tokens_to_add = (elapsed / self.refill_period) * self.max_tokens
            self.tokens[key] = min(self.max_tokens, self.tokens[key] + tokens_to_add)
            self.last_refill[key] = now
        
        # Check if token available
        if self.tokens[key] >= 1.0:
            self.tokens[key] -= 1.0
            return True, int(self.tokens[key])
        else:
            return False, int(self.tokens[key])


class IPRateLimiter:
    """Rate limiter based on IP address"""
    
    def __init__(self, requests_per_hour: int):
        # Convert to token bucket: requests_per_hour tokens refilled every hour
        self.bucket = TokenBucket(max_tokens=requests_per_hour, refill_period_seconds=3600)
        self.request_times: Dict[str, list[float]] = defaultdict(list)
    
    def is_allowed(self, ip: str) -> tuple[bool, int]:
        """
        Check if IP is allowed to make request
        Returns (is_allowed, requests_remaining)
        """
        return self.bucket.is_allowed(ip)

