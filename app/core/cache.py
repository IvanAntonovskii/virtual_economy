import redis.asyncio as redis
import json
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisManager:
    def __init__(self):
        self.redis = None

    async def init_redis(self):
        """Инициализация Redis подключения"""
        try:
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            # Проверка подключения
            await self.redis.ping()
            logger.info("✅ Redis подключен успешно")
        except Exception as e:
            logger.warning(f"❌ Redis недоступен: {e}. Используется заглушка.")
            self.redis = None

    async def get_user_inventory(self, user_id: int):
        if not self.redis:
            return None

        try:
            key = f"user_inventory:{user_id}"
            cached = await self.redis.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error(f"Ошибка получения из кэша: {e}")
        return None

    async def set_user_inventory(self, user_id: int, inventory_data: dict, ttl: int = 300):
        if not self.redis:
            return

        try:
            key = f"user_inventory:{user_id}"
            await self.redis.setex(key, ttl, json.dumps(inventory_data))
        except Exception as e:
            logger.error(f"Ошибка записи в кэш: {e}")

    async def invalidate_user_inventory(self, user_id: int):
        if not self.redis:
            return

        try:
            key = f"user_inventory:{user_id}"
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Ошибка инвалидации кэша: {e}")

    async def clear_all_inventory_cache(self):
        if not self.redis:
            return

        try:
            keys = await self.redis.keys("user_inventory:*")
            if keys:
                await self.redis.delete(*keys)
                logger.info(f"Очищено {len(keys)} ключей инвентаря")
        except Exception as e:
            logger.error(f"Ошибка очистки кэша: {e}")

    async def get_popular_products_cache(self, days: int, limit: int):
        if not self.redis:
            return None

        try:
            key = f"popular_products:{days}:{limit}"
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Ошибка получения аналитики из кэша: {e}")
            return None

    async def set_popular_products_cache(self, days: int, limit: int, data: dict, ttl: int = 3600):
        if not self.redis:
            return

        try:
            key = f"popular_products:{days}:{limit}"
            await self.redis.setex(key, ttl, json.dumps(data))
        except Exception as e:
            logger.error(f"Ошибка записи аналитики в кэш: {e}")


# Глобальный экземпляр
cache_manager = RedisManager()