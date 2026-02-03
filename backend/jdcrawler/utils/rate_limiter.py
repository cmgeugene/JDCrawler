import asyncio
import random


class RateLimiter:
    def __init__(self, delay: float = 3.0, jitter: float = 0.0):
        self.delay = delay
        self.jitter = jitter
        self._last_call = 0.0

    async def acquire(self):
        loop = asyncio.get_event_loop()
        now = loop.time()
        
        # Calculate wait time with jitter
        actual_delay = self.delay + (random.random() * self.jitter)
        
        wait_time = actual_delay - (now - self._last_call)
        if wait_time > 0:
            await asyncio.sleep(wait_time)
            
        self._last_call = loop.time()
