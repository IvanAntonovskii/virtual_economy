import redis.asyncio as redis
from app.core.config import settings

class RedisManager:
    def __init__(self):
        self.redis = None

    async def init_redis(self):
        if not self.redis:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )

    async def get(self, key: str):
        if self.redis:
            return await self.redis.get(key)
        return None

    async def set(self, key: str, value: str, expire: int = 3600):
        if self.redis:
            await self.redis.set(key, value, ex=expire)

    async def delete(self, key: str):
        if self.redis:
            await self.redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.close()

cache_manager = RedisManager()

async def get_user_inventory(user_id: int):
    return await cache_manager.get(f"user_inventory:{user_id}")

async def set_user_inventory(user_id: int, data: str):
    await cache_manager.set(f"user_inventory:{user_id}", data)

async def delete_user_inventory(user_id: int):
    await cache_manager.delete(f"user_inventory:{user_id}")
