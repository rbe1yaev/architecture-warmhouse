from contextlib import asynccontextmanager

import asyncpg
from fastapi import FastAPI

from warmhouse.ms_auth.api import routers
from warmhouse.ms_auth.settings import DB_CONFIG
from warmhouse.ms_auth.utils import DEPS


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    db_pool = await asyncpg.create_pool(**DB_CONFIG)
    DEPS["db"] = db_pool
    yield
    await db_pool.close()


app = FastAPI(
    title="Authentication Service",
    description="Сервис аутентификации и авторизации",
    version="1.0.0",
    lifespan=lifespan,
)


async def init_db():
    conn = await asyncpg.connect(**DB_CONFIG)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id VARCHAR(36) PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            username VARCHAR(100) UNIQUE NOT NULL,
            full_name VARCHAR(255),
            hashed_password TEXT NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_sessions (
            id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) REFERENCES users(id),
            token TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT TRUE
        );
    """)

    await conn.close()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(routers)
