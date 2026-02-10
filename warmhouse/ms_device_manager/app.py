from fastapi import FastAPI
import os
import logging
import httpx
import asyncpg
from contextlib import asynccontextmanager

from warmhouse.ms_device_manager.api import routers

DEPS = {}

# Конфигурация
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "device-manager-db"),
    "port": os.getenv("DB_PORT", 5432),
    "database": os.getenv("DB_NAME", "device_manager"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password")
}

DEVICE_SERVICE_URL = os.getenv("DEVICE_SERVICE_URL", "http://device-service:8002")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация базы данных
    await init_database()
    db_pool = await asyncpg.create_pool(**DB_CONFIG)
    http_client = httpx.AsyncClient(timeout=30.0)

    DEPS["db"] = db_pool
    DEPS["client"] = http_client
    yield

    # Очистка
    await db_pool.close()
    await http_client.aclose()


app = FastAPI(
    title="Device Manager Service",
    description="Управление сценариями и автоматизацией устройств",
    version="1.0.0",
    lifespan=lifespan
)


async def init_database():
    """Инициализация базы данных"""
    conn = await asyncpg.connect(
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        database=DB_CONFIG["database"]
    )

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS scenarios (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            trigger_type VARCHAR(50) NOT NULL,
            cron_schedule VARCHAR(100),
            actions JSONB NOT NULL,
            enabled BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_executed TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS scenario_executions (
            id VARCHAR(36) PRIMARY KEY,
            scenario_id VARCHAR(36) REFERENCES scenarios(id),
            status VARCHAR(20) NOT NULL,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            error_message TEXT
        );

        CREATE TABLE IF NOT EXISTS executed_actions (
            id VARCHAR(36) PRIMARY KEY,
            execution_id VARCHAR(36) REFERENCES scenario_executions(id),
            device_id VARCHAR(255) NOT NULL,
            command TEXT NOT NULL,
            status VARCHAR(20) NOT NULL,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    await conn.close()


@app.get("/health")
async def health_check():
    try:
        async with app.state.db_pool.acquire() as conn:
            await conn.fetchval("SELECT 1")
        return {
            "status": "healthy",
            "service": "device-manager-service",
            "database": "connected"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

app.include_router(routers)