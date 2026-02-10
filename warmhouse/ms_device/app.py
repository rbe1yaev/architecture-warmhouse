from fastapi import FastAPI
import asyncpg
from contextlib import asynccontextmanager

from warmhouse.ms_device.api import routers
from warmhouse.ms_device.depends.dependencies import DEPS
from warmhouse.ms_device.settings import DB_CONFIG



@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    db_pool = await asyncpg.create_pool(**DB_CONFIG)
    DEPS["db"] = db_pool

    yield

    await db_pool.close()


app = FastAPI(
    title="Device Service",
    description="Сервис управления устройствами",
    version="1.0.0",
    lifespan=lifespan
)

# Инициализация БД
async def init_db():
    conn = await asyncpg.connect(**DB_CONFIG)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            device_type VARCHAR(50) NOT NULL,
            status VARCHAR(20) NOT NULL DEFAULT 'offline',
            location VARCHAR(255),
            configuration JSONB DEFAULT '{}',
            metadata JSONB DEFAULT '{}',
            last_seen TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_device_type ON devices(device_type);
        CREATE INDEX IF NOT EXISTS idx_device_status ON devices(status);
        CREATE INDEX IF NOT EXISTS idx_device_location ON devices(location);
    """)

    await conn.close()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

app.include_router(routers)
