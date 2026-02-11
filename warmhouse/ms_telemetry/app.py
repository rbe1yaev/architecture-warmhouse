import logging
from contextlib import asynccontextmanager

import aiohttp
from fastapi import FastAPI

from warmhouse.ms_telemetry.api import routers
from warmhouse.ms_telemetry.settings import CLICKHOUSE_URL
from warmhouse.ms_telemetry.utils import execute_clickhouse_query

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{CLICKHOUSE_URL}/ping") as resp:
                if resp.status == 200:
                    logger.info("Connected to ClickHouse")
                else:
                    logger.error("ClickHouse is not available")
    except Exception as e:
        logger.error(f"Cannot connect to ClickHouse: {e}")

    yield


app = FastAPI(
    title="Telemetry Service",
    description="Сервис сбора и хранения телеметрии",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    try:
        await execute_clickhouse_query("SELECT 1")
        return {
            "status": "healthy",
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


app.include_router(routers)
