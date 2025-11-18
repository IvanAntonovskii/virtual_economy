#!/bin/bash

# Применение миграций
alembic upgrade head

# Инициализация тестовых данных (опционально)
python scripts/init_test_data.py