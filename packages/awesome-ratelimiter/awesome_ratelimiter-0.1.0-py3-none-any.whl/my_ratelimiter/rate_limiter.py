import functools
import time
from collections import deque


def RateLimiter(max_requests: int, period: int, get_key_func=None, token_bucket=True):
    """
    Decorator to apply rate limiting to a function.
    Args:
        max_requests (int): Maximum number of requests allowed in the period.
        period (int): Time period in seconds for the rate limit.
        get_key_func (callable, optional): Function to generate a unique key for each request.
        token_bucket (bool): Use token bucket algorithm if True, otherwise use simple sliding window.
    """
    limiters = {}

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if get_key_func:
                key = get_key_func(*args, **kwargs)
            else:
                key = "default"

            if key not in limiters:
                if token_bucket:
                    limiters[key] = TokenBucketRateLimiter(max_requests, period)
                else:
                    limiters[key] = SlidingWindowRateLimiter(max_requests, period)

            limiter = limiters[key]
            if limiter.allow_request():
                return func(*args, **kwargs)
            else:
                raise RateLimitException(
                    "Rate limit exceeded", limiter.get_retry_after()
                )

        return wrapper

    return decorator


class SlidingWindowRateLimiter:
    """
    A simple rate limiter that allows a maximum number of requests per period.
    based on a sliding window algorithm.
    """

    def __init__(self, max_requests: int, period: int):
        if max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if period <= 0:
            raise ValueError("period must be positive")

        self.max_requests = max_requests
        self.period = period
        self.requests = deque()

    def allow_request(self) -> bool:
        current_time = time.time()

        while self.requests and self.requests[0] < current_time - self.period:
            self.requests.popleft()

        if len(self.requests) < self.max_requests:
            self.requests.append(current_time)
            return True
        return False

    def get_retry_after(self) -> float:
        """Returns the time to wait before the next request can be made."""
        if not self.requests:
            return 0.0

        oldest_request_time = self.requests[0]
        next_allowed_time = oldest_request_time + self.period
        wait_time = next_allowed_time - time.time()
        return max(0, wait_time)


class TokenBucketRateLimiter:
    """
    A token bucket rate limiter.
    It allows a maximum number of tokens to be consumed per period.
    """

    def __init__(self, capacity: int, period: float):
        if capacity <= 0:
            raise ValueError("capacity must be positive")

        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = capacity / period
        self.last_refill_time = time.time()

    def allow_request(self) -> bool:

        # Refill tokens based on elapsed time
        self._refill()

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False

    def _refill(self):
        current_time = time.time()
        elapsed_time = current_time - self.last_refill_time
        new_tokens = elapsed_time * self.refill_rate
        # print(f"Refilling tokens: {new_tokens:.2f} added, current tokens: {self.tokens:.2f}")
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill_time = current_time

    def get_retry_after(self) -> float:
        """Returns the time to wait before the next request can be made."""
        if self.tokens >= 1:
            return 0.0  # No wait needed

        # Calculate time needed to generate enough tokens to reach 1.0
        tokens_needed = 1.0 - self.tokens
        wait_time = tokens_needed / self.refill_rate
        return wait_time


class RateLimitException(Exception):
    """Custom exception for rate limit exceeded."""

    def __init__(self, message, delay):
        super().__init__(message)
        self.delay = delay


@RateLimiter(max_requests=5, period=10, token_bucket=True)
def fetch_global_data():
    print(f"[{time.strftime('%H:%M:%S')}] Successfully fetched global data.")


print("--- Testing Global Rate Limiter ---")
for i in range(8):
    try:
        fetch_global_data()
    except RateLimitException as e:
        print(
            f"[{time.strftime('%H:%M:%S')}] Rate limited! Try again in {e.delay:.2f} seconds."
        )
    time.sleep(0.1)

"""
    --- Testing Global Rate Limiter ---
# [00:22:46] Successfully fetched global data.
# [00:22:46] Successfully fetched global data.
# [00:22:46] Successfully fetched global data.
# [00:22:46] Successfully fetched global data.
# [00:22:46] Successfully fetched global data.
# [00:22:46] Rate limited! Try again in 1.50 seconds.
# [00:22:46] Rate limited! Try again in 1.40 seconds.
# [00:22:46] Rate limited! Try again in 1.30 seconds.

"""


@RateLimiter(max_requests=5, period=10, token_bucket=False)
def fetch_global_data():
    print(f"[{time.strftime('%H:%M:%S')}] Successfully fetched global data.")


print("--- Testing Global Rate Limiter ---")
for i in range(8):
    try:
        fetch_global_data()
    except RateLimitException as e:
        print(
            f"[{time.strftime('%H:%M:%S')}] Rate limited! Try again in {e.delay:.2f} seconds."
        )
    time.sleep(0.1)

""""
--- Testing Global Rate Limiter ---
[00:22:55] Successfully fetched global data.
[00:22:55] Successfully fetched global data.
[00:22:55] Successfully fetched global data.
[00:22:55] Successfully fetched global data.
[00:22:55] Successfully fetched global data.
[00:22:55] Rate limited! Try again in 9.50 seconds.
[00:22:55] Rate limited! Try again in 9.40 seconds.
[00:22:55] Rate limited! Try again in 9.30 seconds.

"""
