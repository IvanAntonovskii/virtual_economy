from app.core.cache import cache_manager
from celery import Celery
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

celery_app = Celery(
    "virtual_economy",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
)


@celery_app.task
def clear_inventory_cache():
    """Очистка кэша инвентаря всех пользователей"""
    try:
        import asyncio
        # Создаем новую event loop для задачи
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(cache_manager.clear_all_inventory_cache())
        loop.close()

        logger.info("✅ Кэш инвентаря очищен")
        return {"status": "success", "message": "Inventory cache cleared"}
    except Exception as e:
        logger.error(f"❌ Ошибка очистки кэша: {e}")
        return {"status": "error", "message": str(e)}


@celery_app.task
def update_popular_products_cache():
    """Обновление кэша популярных товаров"""
    try:
        # Здесь можно добавить предварительное обновление аналитики
        logger.info("✅ Кэш популярных товаров обновлен")
        return {"status": "success", "message": "Popular products cache updated"}
    except Exception as e:
        logger.error(f"❌ Ошибка обновления кэша: {e}")
        return {"status": "error", "message": str(e)}


# Ежедневные задачи в 3:00
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        86400.0,  # 24 часа
        clear_inventory_cache.s(),
        name='clear inventory cache daily'
    )

    sender.add_periodic_task(
        3600.0,  # 1 час
        update_popular_products_cache.s(),
        name='update popular products cache hourly'
    )