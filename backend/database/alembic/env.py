import os
from logging.config import fileConfig
from dotenv import load_dotenv

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# ────────────────────────────────────────────────
# Загружаем .env файл (если он существует)
# ────────────────────────────────────────────────
load_dotenv()  # автоматически ищет .env в корне проекта

# ────────────────────────────────────────────────
# Alembic Config объект (доступ к alembic.ini)
# ────────────────────────────────────────────────
config = context.config

# Если в alembic.ini нет sqlalchemy.url — берём из .env
if not config.get_main_option("sqlalchemy.url"):
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL не найден ни в alembic.ini, ни в .env файле")
    config.set_main_option("sqlalchemy.url", db_url)

# Настройка логирования из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ────────────────────────────────────────────────
# Подключаем твои модели
# ────────────────────────────────────────────────
from backend.database.models import Base

target_metadata = Base.metadata


# ────────────────────────────────────────────────
# Оффлайн-режим (генерация SQL без подключения к БД)
# ────────────────────────────────────────────────
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# ────────────────────────────────────────────────
# Онлайн-режим (реальное применение миграций)
# ────────────────────────────────────────────────
def run_migrations_online() -> None:
    """Запуск миграций в онлайн-режиме (с подключением к БД)"""

    # Используем синхронный engine — Alembic работает с ним отлично
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Синхронный контекст-менеджер работает без проблем
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()

    # Закрываем пул (хорошая практика)
    connectable.dispose()


# ────────────────────────────────────────────────
# Выбор режима запуска
# ────────────────────────────────────────────────
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()