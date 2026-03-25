from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from backend.database.database import engine, get_session, init_db  # ← engine нужен для проверки
from backend.routers.api import api_router


# Настраиваем базовое логирование (можно позже заменить на structlog или loguru)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SavorLink API...")

    try:
        # Правильная проверка подключения
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))          # ← вот здесь text()
            await conn.commit()                           # опционально, но полезно

        logger.info("Database connection successful")

        await init_db()
        logger.info("Database tables initialized / already exist")

    except Exception as e:
        logger.error("Database initialization or connection failed", exc_info=True)

    yield

    logger.info("Shutting down SavorLink API...")
    await engine.dispose()
    logger.info("Database engine disposed")


# ──────────────────────────────────────────────────────────────
#  FastAPI приложение
# ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="SavorLink API",
    description="Marketplace for connecting suppliers and buyers (SavorLink MVP)",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    # openapi_url=None,          # можно отключить в продакшене
)


# CORS — разрешаем фронтенд (Vite/React обычно на 5173)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # "https://your-frontend-domain.com",  # добавь позже
    # "*"  # ← только для отладки, в продакшене не используй
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключаем все роутеры
app.include_router(api_router)


@app.get("/")
async def read_root():
    """Корневой эндпоинт — приветственное сообщение"""
    return {"message": "Welcome to SavorLink API"}


if __name__ == "__main__":
    import uvicorn

    # Настройки запуска — удобно менять через .env или аргументы
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,                # авто-перезапуск при изменении кода
        log_level="info",           # или "debug" для большей детализации
        # workers=1,                # можно раскомментировать в продакшене
    )