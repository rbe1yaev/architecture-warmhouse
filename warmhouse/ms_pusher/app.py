from fastapi import FastAPI
import os
import logging
from contextlib import asynccontextmanager
import asyncio

from warmhouse.ms_pusher.services.pusher import consume_notifications


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск Kafka consumer
    kafka_consumer_task = asyncio.create_task(consume_notifications())
    yield
    kafka_consumer_task.cancel()


app = FastAPI(
    title="Notification Service",
    description="Сервис уведомлений и WebSocket соединений",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
    }



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8005)