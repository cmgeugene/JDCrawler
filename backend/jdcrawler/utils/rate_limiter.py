import asyncio


class RateLimiter:
    def __init__(self, delay: float = 3.0):
        self.delay = delay
        self._last_call = 0.0

    async def acquire(self):
        loop = asyncio.get_event_loop()
        now = loop.time()
        if now - self._last_call < self.delay:
            await asyncio.sleep(self.delay - (now - self._last_call))
        self._last_call = loop.time()
