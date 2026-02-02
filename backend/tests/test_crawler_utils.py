import asyncio

import pytest

from jdcrawler.utils.rate_limiter import RateLimiter
from jdcrawler.utils.retry import retry


class TestRateLimiter:
    @pytest.mark.asyncio
    async def test_rate_limiter_delays(self):
        rate_limiter = RateLimiter(delay=0.1)
        start = asyncio.get_event_loop().time()
        await rate_limiter.acquire()
        await rate_limiter.acquire()
        elapsed = asyncio.get_event_loop().time() - start
        assert elapsed >= 0.1


class TestRetryDecorator:
    @pytest.mark.asyncio
    async def test_retry_succeeds_on_first_attempt(self):
        call_count = 0

        @retry(max_attempts=3, delay=0.01)
        async def failing_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await failing_func()
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_retries_on_failure(self):
        call_count = 0

        @retry(max_attempts=3, delay=0.01)
        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"

        result = await failing_func()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_raises_after_max_attempts(self):
        call_count = 0

        @retry(max_attempts=2, delay=0.01)
        async def failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")

        with pytest.raises(ValueError):
            await failing_func()
        assert call_count == 2
