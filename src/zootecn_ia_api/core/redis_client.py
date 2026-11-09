from typing import Optional

import redis.asyncio as redis

class RedisManager:
    _instance: Optional[redis.Redis] = None

    @classmethod
    def get_client(cls) -> redis.Redis:
        if cls._instance is None:
            cls._instance = redis.Redis.from_url(
                "redis://localhost:6379/0", 
                decode_responses=True
            )
        return cls._instance