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


# CORS — временно разрешаем ВСЁ для отладки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Глобальный обработчик ошибок для отладки
@app.middleware("http")
async def catch_exceptions_middleware(request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "exception": str(e)},
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
            }
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