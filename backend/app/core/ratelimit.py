import time
from fastapi import Request, HTTPException, status
import redis.asyncio as redis

# Default limits: 10 requests per 60-second window
DEFAULT_RATE_LIMIT = 10
WINDOW_SIZE_SECONDS = 60


class RedisRateLimiter:
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)

    async def check_rate_limit(
        self, 
        request: Request, 
        limit: int = DEFAULT_RATE_LIMIT, 
        window: int = WINDOW_SIZE_SECONDS
    ):
        """
        Sliding window rate-limiter using Redis sorted sets (ZSET).
        """
        # Determine client identity (IP address or fallback)
        client_ip = request.client.host if request.client else "127.0.0.1"
        key = f"rate_limit:{client_ip}:{request.url.path}"

        current_time = time.time()
        window_start = current_time - window

        async with self.redis_client.pipeline(transaction=True) as pipe:
            # 1. Clear timestamps older than the sliding window
            pipe.zremrangebyscore(key, 0, window_start)
            # 2. Count requests in the current window
            pipe.zcard(key)
            # 3. Add current request timestamp
            pipe.zadd(key, {str(current_time): current_time})
            # 4. Set key expiration to keep Redis clean
            pipe.expire(key, window)
            
            _, request_count, _, _ = await pipe.execute()

        # If requests exceed the limit, reject with 429 Too Many Requests
        if request_count >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {limit} requests allowed per {window} seconds."
            )

    async def close(self):
        await self.redis_client.close()